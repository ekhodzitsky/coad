from __future__ import annotations

from pathlib import Path
from typing import Any

from .report import versioned_report
from .report_sources import (
    CORE_METHODOLOGY_SOURCES,
    ONBOARDING_METHODOLOGY_SOURCES,
    ReportSource,
)
from .validate import find_schema_dir, validate_path

EXECUTION_CONTRACT_KINDS = {
    "goal_contract",
    "task_contract",
    "proof_contract",
    "handoff_contract",
    "integration_contract",
    "review_contract",
}


def build_check_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    resolved_root = root.resolve()
    resolved_schema_dir = (schema_dir or find_schema_dir(resolved_root)).resolve()
    sources = _applicable_sources(resolved_root, resolved_schema_dir)
    issues: list[dict[str, str]] = []
    checks = [
        _check_source(source, resolved_root, resolved_schema_dir, issues)
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


def _applicable_sources(root: Path, schema_dir: Path) -> list[ReportSource]:
    report = validate_path(root, schema_dir=schema_dir, check_graph=False)
    if any(document.kind in EXECUTION_CONTRACT_KINDS for document in report.documents):
        return CORE_METHODOLOGY_SOURCES
    return ONBOARDING_METHODOLOGY_SOURCES


def _check_source(
    source: ReportSource,
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


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
