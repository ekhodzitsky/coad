from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .drift import build_drift_report
from .graph_report import build_graph_report
from .ledger import build_ledger_report
from .policy import build_policy_report
from .profile import build_profile_report
from .proof_matrix import build_proof_matrix
from .report import versioned_report
from .schedule import build_schedule_report
from .status import build_status_report
from .validate import validate_path


@dataclass(frozen=True)
class AttestationSource:
    name: str
    producer: str
    required: bool
    build: Callable[[Path, Path], dict[str, Any]]


SOURCES = [
    AttestationSource("validation-report", "coad-validate", True, lambda root, schema_dir: _validation_report(root, schema_dir)),
    AttestationSource("status-report", "coad-status", True, lambda root, schema_dir: build_status_report(root, schema_dir=schema_dir)),
    AttestationSource("proof-matrix", "coad-proof-matrix", True, lambda root, schema_dir: build_proof_matrix(root, schema_dir=schema_dir)),
    AttestationSource("graph-report", "coad-graph", True, lambda root, schema_dir: build_graph_report(root, schema_dir=schema_dir)),
    AttestationSource("schedule-report", "coad-schedule", True, lambda root, schema_dir: build_schedule_report(root, schema_dir=schema_dir)),
    AttestationSource("ledger-report", "coad-ledger", True, lambda root, schema_dir: build_ledger_report(root, schema_dir=schema_dir)),
    AttestationSource("profile-report", "coad-profile", True, lambda root, schema_dir: build_profile_report(root, schema_dir=schema_dir)),
    AttestationSource("policy-report", "coad-policy", True, lambda root, schema_dir: build_policy_report(root, schema_dir=schema_dir)),
    AttestationSource("drift-report", "coad-drift", True, lambda root, _schema_dir: build_drift_report(root)),
]


def build_attestation_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    resolved_root = root.resolve()
    resolved_schema_dir = (schema_dir or resolved_root / "schema").resolve()
    issues: list[dict[str, str]] = []
    reports = [
        _attested_report(source, resolved_root, resolved_schema_dir, issues)
        for source in SOURCES
    ]
    bundle_digest = _sha256(
        {
            "reports": [
                {
                    "name": report["name"],
                    "digest": report["digest"],
                    "ok": report["ok"],
                    "required": report["required"],
                }
                for report in reports
            ]
        }
    )
    return versioned_report(
        {
            "ok": not issues,
            "status": "attested" if not issues else "attestation_failed",
            "bundle_digest": bundle_digest,
            "reports": reports,
            "issues": issues,
        }
    )


def _attested_report(
    source: AttestationSource,
    root: Path,
    schema_dir: Path,
    issues: list[dict[str, str]],
) -> dict[str, Any]:
    payload = source.build(root, schema_dir)
    ok = payload.get("ok") is True
    if source.required and not ok:
        issues.append(
            {
                "severity": "error",
                "path": _issue_path(payload, root),
                "message": f"required attestation report failed: {source.name}",
            }
        )
    status = payload.get("status")
    return {
        "name": source.name,
        "producer": source.producer,
        "required": source.required,
        "ok": ok,
        "status": status if isinstance(status, str) else "",
        "digest": _sha256(payload),
    }


def _validation_report(root: Path, schema_dir: Path) -> dict[str, Any]:
    report = validate_path(root, schema_dir=schema_dir)
    return versioned_report(
        {
            "contracts": len(report.documents),
            "issues": [issue.to_json(report.root) for issue in report.issues],
            "ok": report.ok,
        }
    )


def _issue_path(payload: dict[str, Any], root: Path) -> str:
    issues = payload.get("issues")
    if isinstance(issues, list):
        for issue in issues:
            if not isinstance(issue, dict):
                continue
            path = issue.get("path")
            if isinstance(path, str) and path:
                return path
    return _relative_path(root, root)


def _sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
