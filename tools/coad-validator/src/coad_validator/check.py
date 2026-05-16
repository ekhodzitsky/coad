from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .graph_report import build_graph_report
from .ledger import build_ledger_report
from .policy import build_policy_report
from .proof_matrix import build_proof_matrix
from .report import versioned_report
from .schedule import build_schedule_report
from .status import build_status_report
from .validate import find_schema_dir, validate_path


@dataclass(frozen=True)
class CheckSource:
    name: str
    producer: str
    required: bool
    build: Callable[[Path, Path], dict[str, Any]]


CHECK_SOURCES = [
    CheckSource(
        "validation-report",
        "coad-validate",
        True,
        lambda root, schema_dir: _validation_report(root, schema_dir),
    ),
    CheckSource(
        "status-report",
        "coad-status",
        True,
        lambda root, schema_dir: build_status_report(root, schema_dir=schema_dir),
    ),
    CheckSource(
        "proof-matrix",
        "coad-proof-matrix",
        True,
        lambda root, schema_dir: build_proof_matrix(root, schema_dir=schema_dir),
    ),
    CheckSource(
        "graph-report",
        "coad-graph",
        True,
        lambda root, schema_dir: build_graph_report(root, schema_dir=schema_dir),
    ),
    CheckSource(
        "schedule-report",
        "coad-schedule",
        True,
        lambda root, schema_dir: build_schedule_report(root, schema_dir=schema_dir),
    ),
    CheckSource(
        "ledger-report",
        "coad-ledger",
        True,
        lambda root, schema_dir: build_ledger_report(root, schema_dir=schema_dir),
    ),
    CheckSource(
        "policy-report",
        "coad-policy",
        True,
        lambda root, schema_dir: build_policy_report(root, schema_dir=schema_dir),
    ),
]


def build_check_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    resolved_root = root.resolve()
    resolved_schema_dir = (schema_dir or find_schema_dir(resolved_root)).resolve()
    issues: list[dict[str, str]] = []
    checks = [
        _check_source(source, resolved_root, resolved_schema_dir, issues)
        for source in CHECK_SOURCES
    ]
    ok = not issues
    return versioned_report(
        {
            "ok": ok,
            "status": "pass" if ok else "fail",
            "checks": checks,
            "issues": issues,
        }
    )


def _check_source(
    source: CheckSource,
    root: Path,
    schema_dir: Path,
    issues: list[dict[str, str]],
) -> dict[str, Any]:
    payload = source.build(root, schema_dir)
    ok = payload.get("ok") is True
    if source.required and not ok:
        _extend_issues(issues, payload, source.name, root)
    status = payload.get("status")
    return {
        "name": source.name,
        "producer": source.producer,
        "required": source.required,
        "ok": ok,
        "status": status if isinstance(status, str) else "",
    }


def _extend_issues(
    issues: list[dict[str, str]],
    payload: dict[str, Any],
    source_name: str,
    root: Path,
) -> None:
    payload_issues = payload.get("issues")
    if isinstance(payload_issues, list) and payload_issues:
        for issue in payload_issues:
            if not isinstance(issue, dict):
                continue
            path = issue.get("path")
            message = issue.get("message")
            severity = issue.get("severity")
            issues.append(
                {
                    "severity": severity if isinstance(severity, str) else "error",
                    "path": path if isinstance(path, str) else _relative_path(root, root),
                    "message": (
                        f"{source_name}: {message}"
                        if isinstance(message, str)
                        else f"{source_name} failed"
                    ),
                }
            )
        return
    issues.append(
        {
            "severity": "error",
            "path": _relative_path(root, root),
            "message": f"{source_name} failed",
        }
    )


def _validation_report(root: Path, schema_dir: Path) -> dict[str, Any]:
    report = validate_path(root, schema_dir=schema_dir)
    return versioned_report(
        {
            "contracts": len(report.documents),
            "issues": [issue.to_json(report.root) for issue in report.issues],
            "ok": report.ok,
        }
    )


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
