from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .graph_report import build_graph_report
from .ledger import build_ledger_report
from .policy import build_policy_report
from .proof_matrix import build_proof_matrix
from .report import versioned_report
from .report_sources import (
    CORE_METHODOLOGY_SOURCES,
    ONBOARDING_METHODOLOGY_SOURCES,
    ReportSource,
)
from .schedule import build_schedule_report
from .status import build_status_report
from .validate import ValidationReport, find_schema_dir, validate_path

EXECUTION_CONTRACT_KINDS = {
    "goal_contract",
    "task_contract",
    "proof_contract",
    "handoff_contract",
    "integration_contract",
    "review_contract",
}

CachedSourceBuilder = Callable[..., dict[str, Any]]

_CACHED_SOURCE_BUILDERS: dict[str, CachedSourceBuilder] = {
    "status-report": build_status_report,
    "proof-matrix": build_proof_matrix,
    "graph-report": build_graph_report,
    "schedule-report": build_schedule_report,
    "ledger-report": build_ledger_report,
    "policy-report": build_policy_report,
}


def build_check_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    resolved_root = root.resolve()
    resolved_schema_dir = (schema_dir or find_schema_dir(resolved_root)).resolve()
    validation_report = validate_path(resolved_root, schema_dir=resolved_schema_dir)
    sources = _applicable_sources(validation_report)
    issues: list[dict[str, str]] = []
    checks = [
        _check_source(source, resolved_root, resolved_schema_dir, validation_report, issues)
        for source in sources
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


def _applicable_sources(report: ValidationReport) -> list[ReportSource]:
    if any(document.kind in EXECUTION_CONTRACT_KINDS for document in report.documents):
        return CORE_METHODOLOGY_SOURCES
    return ONBOARDING_METHODOLOGY_SOURCES


def _check_source(
    source: ReportSource,
    root: Path,
    schema_dir: Path,
    validation_report: ValidationReport,
    issues: list[dict[str, str]],
) -> dict[str, Any]:
    payload = _source_payload(source, root, schema_dir, validation_report)
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


def _source_payload(
    source: ReportSource,
    root: Path,
    schema_dir: Path,
    validation_report: ValidationReport,
) -> dict[str, Any]:
    if source.name == "validation-report":
        return _validation_payload(validation_report)
    cached_builder = _CACHED_SOURCE_BUILDERS.get(source.name)
    if cached_builder is not None:
        return cached_builder(root, schema_dir=schema_dir, contract_report=validation_report)
    return source.build(root, schema_dir)


def _validation_payload(report: ValidationReport) -> dict[str, Any]:
    return versioned_report(
        {
            "contracts": len(report.documents),
            "issues": [issue.to_json(report.root) for issue in report.issues],
            "ok": report.ok,
        }
    )


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
            code = issue.get("code")
            issues.append(
                {
                    "code": code if isinstance(code, str) else f"{source_name}.failed",
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
            "code": f"{source_name}.failed",
            "severity": "error",
            "path": _relative_path(root, root),
            "message": f"{source_name} failed",
        }
    )


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
