from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .drift import build_drift_report
from .ledger import build_ledger_report
from .report import versioned_report
from .schedule import build_schedule_report
from .validate import find_schema_dir, validate_path


@dataclass(frozen=True)
class ProfileIssue:
    path: Path
    message: str
    severity: str = "error"

    def to_json(self, root: Path) -> dict[str, str]:
        return {
            "severity": self.severity,
            "path": _relative_path(self.path, root),
            "message": self.message,
        }


def build_profile_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    resolved_root = root.resolve()
    resolved_schema_dir = (schema_dir or find_schema_dir(resolved_root)).resolve()
    issues: list[ProfileIssue] = []
    profile_path = resolved_root / "COAD_PROFILE.json"
    profile = _load_profile(profile_path, resolved_schema_dir, issues)

    checks = [
        _evaluate_check(check, resolved_root, resolved_schema_dir)
        for check in _profile_checks(profile)
    ]
    for check in checks:
        if check["required"] and check["status"] != "pass":
            issues.append(ProfileIssue(profile_path, f"required profile check failed: {check['id']}"))

    return versioned_report(
        {
            "ok": not issues,
            "status": "conformant" if not issues else "nonconformant",
            "profile_id": _string_value(profile.get("profile_id")),
            "level": _string_value(profile.get("level")),
            "checks": checks,
            "issues": [issue.to_json(resolved_root) for issue in issues],
        }
    )


def _load_profile(
    path: Path,
    schema_dir: Path,
    issues: list[ProfileIssue],
) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(ProfileIssue(path, "missing conformance profile"))
        return {}
    except json.JSONDecodeError as exc:
        issues.append(ProfileIssue(path, f"invalid conformance profile JSON: {exc.msg}"))
        return {}

    schema_path = schema_dir / "conformance-profile.schema.json"
    if not schema_path.is_file():
        issues.append(ProfileIssue(schema_path, "missing conformance profile schema"))
        return payload if isinstance(payload, dict) else {}

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(payload), key=str):
        location = ".".join(str(part) for part in error.absolute_path)
        prefix = f"profile schema violation at {location}: " if location else "profile schema violation: "
        issues.append(ProfileIssue(path, prefix + error.message))

    if not isinstance(payload, dict):
        issues.append(ProfileIssue(path, "conformance profile must be a JSON object"))
        return {}
    return payload


def _profile_checks(profile: dict[str, Any]) -> list[dict[str, Any]]:
    checks = profile.get("checks")
    if not isinstance(checks, list):
        return []
    return [check for check in checks if isinstance(check, dict)]


def _evaluate_check(check: dict[str, Any], root: Path, schema_dir: Path) -> dict[str, Any]:
    check_id = _string_value(check.get("id"))
    required = check.get("required")
    is_required = required if isinstance(required, bool) else False
    status, evidence = _check_status(check_id, root, schema_dir)
    return {
        "id": check_id,
        "status": status,
        "required": is_required,
        "evidence": evidence,
    }


def _check_status(check_id: str, root: Path, schema_dir: Path) -> tuple[str, str]:
    if check_id == "contracts-valid":
        report = validate_path(root, schema_dir=schema_dir)
        return ("pass" if report.ok else "fail"), f"coad-validate ok={str(report.ok).lower()}"
    if check_id == "schedule-builds":
        report = build_schedule_report(root, schema_dir=schema_dir)
        return ("pass" if report["ok"] else "fail"), f"coad-schedule status={report['status']}"
    if check_id == "execution-ledger-verified":
        report = build_ledger_report(root, schema_dir=schema_dir)
        return ("pass" if report["ok"] else "fail"), f"coad-ledger status={report['status']}"
    if check_id == "release-gates-clean":
        report = build_drift_report(root)
        return ("pass" if report["ok"] else "fail"), f"coad-drift status={report['status']}"
    return "unknown", "unknown profile check"


def _string_value(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
