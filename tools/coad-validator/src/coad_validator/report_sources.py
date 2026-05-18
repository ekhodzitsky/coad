from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .agent_guidance import build_agent_guidance_report
from .contract_update_integrity import build_contract_update_integrity_report
from .drift import build_drift_report
from .graph_report import build_graph_report
from .handoff_integrity import build_handoff_integrity_report
from .ledger import build_ledger_report
from .policy import build_policy_report
from .profile import build_profile_report
from .proof_artifact_integrity import build_proof_artifact_integrity_report
from .proof_matrix import build_proof_matrix
from .proof_result_integrity import build_proof_result_integrity_report
from .report import versioned_report
from .schedule import build_schedule_report
from .status import build_status_report
from .task_scope_integrity import build_task_scope_integrity_report
from .validate import ValidationReport, validate_path

COAD_CHECK_PRODUCER = "coad check"


@dataclass(frozen=True)
class ReportSource:
    name: str
    producer: str
    required: bool
    build: Callable[[Path, Path], dict[str, Any]]


CORE_METHODOLOGY_SOURCES = [
    ReportSource(
        "agent-guidance",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_agent_guidance_report(root, schema_dir),
    ),
    ReportSource(
        "validation-report",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_validation_report(root, schema_dir),
    ),
    ReportSource(
        "status-report",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_status_report(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "proof-matrix",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_proof_matrix(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "graph-report",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_graph_report(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "schedule-report",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_schedule_report(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "ledger-report",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_ledger_report(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "policy-report",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_policy_report(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "handoff-integrity",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_handoff_integrity_report(root, schema_dir),
    ),
    ReportSource(
        "task-scope-integrity",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_task_scope_integrity_report(root, schema_dir),
    ),
    ReportSource(
        "proof-result-integrity",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_proof_result_integrity_report(root, schema_dir),
    ),
    ReportSource(
        "contract-update-integrity",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_contract_update_integrity_report(root, schema_dir),
    ),
    ReportSource(
        "proof-artifact-integrity",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_proof_artifact_integrity_report(root, schema_dir),
    ),
]

ONBOARDING_METHODOLOGY_SOURCES = CORE_METHODOLOGY_SOURCES[:2]

ATTESTATION_SOURCES = [
    *CORE_METHODOLOGY_SOURCES,
    ReportSource(
        "profile-report",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, schema_dir: build_profile_report(root, schema_dir=schema_dir),
    ),
    ReportSource(
        "drift-report",
        COAD_CHECK_PRODUCER,
        True,
        lambda root, _schema_dir: build_drift_report(root),
    ),
]


def build_validation_report(root: Path, schema_dir: Path) -> dict[str, Any]:
    report = validate_path(root, schema_dir=schema_dir)
    return build_validation_payload(report)


def build_source_payload(
    source: ReportSource,
    root: Path,
    schema_dir: Path,
    contract_report: ValidationReport | None = None,
) -> dict[str, Any]:
    if contract_report is None:
        return source.build(root, schema_dir)
    if source.name == "validation-report":
        return build_validation_payload(contract_report)
    cached_builder = _CACHED_SOURCE_BUILDERS.get(source.name)
    if cached_builder is not None:
        return cached_builder(root, schema_dir, contract_report)
    return source.build(root, schema_dir)


def build_validation_payload(report: ValidationReport) -> dict[str, Any]:
    return versioned_report(
        {
            "contracts": len(report.documents),
            "issues": [issue.to_json(report.root) for issue in report.issues],
            "ok": report.ok,
        }
    )


_CACHED_SOURCE_BUILDERS: dict[str, Callable[[Path, Path, ValidationReport], dict[str, Any]]] = {
    "status-report": lambda root, schema_dir, report: build_status_report(
        root,
        schema_dir=schema_dir,
        contract_report=report,
    ),
    "proof-matrix": lambda root, schema_dir, report: build_proof_matrix(
        root,
        schema_dir=schema_dir,
        contract_report=report,
    ),
    "graph-report": lambda root, schema_dir, report: build_graph_report(
        root,
        schema_dir=schema_dir,
        contract_report=report,
    ),
    "schedule-report": lambda root, schema_dir, report: build_schedule_report(
        root,
        schema_dir=schema_dir,
        contract_report=report,
    ),
    "ledger-report": lambda root, schema_dir, report: build_ledger_report(
        root,
        schema_dir=schema_dir,
        contract_report=report,
    ),
    "policy-report": lambda root, schema_dir, report: build_policy_report(
        root,
        schema_dir=schema_dir,
        contract_report=report,
    ),
    "handoff-integrity": lambda root, schema_dir, report: build_handoff_integrity_report(
        root,
        schema_dir,
        report,
    ),
    "task-scope-integrity": lambda root, schema_dir, report: build_task_scope_integrity_report(
        root,
        schema_dir,
        report,
    ),
    "proof-result-integrity": lambda root, schema_dir, report: build_proof_result_integrity_report(
        root,
        schema_dir,
        report,
    ),
    "contract-update-integrity": lambda root, schema_dir, report: build_contract_update_integrity_report(
        root,
        schema_dir,
        report,
    ),
    "proof-artifact-integrity": lambda root, schema_dir, report: build_proof_artifact_integrity_report(
        root,
        schema_dir,
        report,
    ),
    "profile-report": lambda root, schema_dir, report: build_profile_report(
        root,
        schema_dir=schema_dir,
        contract_report=report,
    ),
}
