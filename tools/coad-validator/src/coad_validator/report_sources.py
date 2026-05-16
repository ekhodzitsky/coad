from __future__ import annotations

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
class ReportSource:
    name: str
    producer: str
    required: bool
    build: Callable[[Path, Path], dict[str, Any]]


CORE_METHODOLOGY_SOURCES = [
    ReportSource(
        "validation-report",
        "coad-validate",
        True,
        lambda root, schema_dir: build_validation_report(root, schema_dir),
    ),
    ReportSource(
        "status-report",
        "coad-status",
        True,
        lambda root, schema_dir: build_status_report(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "proof-matrix",
        "coad-proof-matrix",
        True,
        lambda root, schema_dir: build_proof_matrix(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "graph-report",
        "coad-graph",
        True,
        lambda root, schema_dir: build_graph_report(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "schedule-report",
        "coad-schedule",
        True,
        lambda root, schema_dir: build_schedule_report(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "ledger-report",
        "coad-ledger",
        True,
        lambda root, schema_dir: build_ledger_report(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "policy-report",
        "coad-policy",
        True,
        lambda root, schema_dir: build_policy_report(root, schema_dir=schema_dir),
    ),
]

ATTESTATION_SOURCES = [
    *CORE_METHODOLOGY_SOURCES,
    ReportSource(
        "profile-report",
        "coad-profile",
        True,
        lambda root, schema_dir: build_profile_report(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "drift-report",
        "coad-drift",
        True,
        lambda root, _schema_dir: build_drift_report(root),
    ),
]


def build_validation_report(root: Path, schema_dir: Path) -> dict[str, Any]:
    report = validate_path(root, schema_dir=schema_dir)
    return versioned_report(
        {
            "contracts": len(report.documents),
            "issues": [issue.to_json(report.root) for issue in report.issues],
            "ok": report.ok,
        }
    )
