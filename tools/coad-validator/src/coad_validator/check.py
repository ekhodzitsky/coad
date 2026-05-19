from __future__ import annotations

from pathlib import Path
from typing import Any

from .report import versioned_report
from .report_sources import (
    CORE_METHODOLOGY_SOURCES,
    ONBOARDING_METHODOLOGY_SOURCES,
    ReportSource,
    build_source_payload,
)
from .validate import ValidationReport, find_schema_dir, validate_path

EXECUTION_CONTRACT_KINDS = {
    "goal_contract",
    "task_contract",
    "proof_contract",
    "handoff_contract",
    "integration_contract",
    "review_contract",
}

CONTINUE_STATUSES = {"partial", "unknown", "weak", "warning"}
PHASE_BY_SOURCE_CHECK = {
    "agent-guidance": "orient",
    "validation-report": "orient",
    "status-report": "orient",
    "proof-matrix": "orient",
    "graph-report": "orient",
    "schedule-report": "orient",
    "ledger-report": "execute",
    "policy-report": "scope",
    "handoff-integrity": "execute",
    "task-scope-integrity": "execute",
    "ledger-handoff-integrity": "execute",
    "proof-result-integrity": "prove",
    "proof-artifact-integrity": "prove",
    "contract-update-integrity": "update_knowledge",
    "methodology-loop": "orient",
}


def build_check_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    resolved_root = root.resolve()
    resolved_schema_dir = (schema_dir or find_schema_dir(resolved_root)).resolve()
    validation_report = validate_path(resolved_root, schema_dir=resolved_schema_dir)
    sources = _applicable_sources(validation_report)
    issues: list[dict[str, str]] = []
    source_payloads = [
        (source, _source_payload(source, resolved_root, resolved_schema_dir, validation_report))
        for source in sources
    ]
    checks = [_check_source(source, payload, resolved_root, issues) for source, payload in source_payloads]
    blocking_checks = _blocking_checks(checks)
    next_actions = _next_actions(source_payloads)
    ok = not issues
    return versioned_report(
        {
            "ok": ok,
            "status": "pass" if ok else "fail",
            "agent_status": _agent_status(checks, blocking_checks, next_actions),
            "blocking_checks": blocking_checks,
            "next_actions": next_actions,
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
    payload: dict[str, Any],
    root: Path,
    issues: list[dict[str, str]],
) -> dict[str, Any]:
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
    return build_source_payload(source, root, schema_dir, validation_report)


def _blocking_checks(checks: list[dict[str, Any]]) -> list[str]:
    return [
        str(check["name"])
        for check in checks
        if check.get("required") is True and check.get("ok") is not True
    ]


def _agent_status(
    checks: list[dict[str, Any]],
    blocking_checks: list[str],
    next_actions: list[dict[str, Any]],
) -> str:
    if blocking_checks:
        if any(action["blocks_completion"] for action in next_actions):
            return "repair_required"
        return "blocked"
    if any(_check_needs_agent_attention(check) for check in checks):
        return "continue"
    return "pass"


def _check_needs_agent_attention(check: dict[str, Any]) -> bool:
    status = check.get("status")
    if status in CONTINUE_STATUSES:
        return True
    return check.get("name") == "methodology-loop" and status == "skipped"


def _next_actions(source_payloads: list[tuple[ReportSource, dict[str, Any]]]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for source, payload in source_payloads:
        issues = payload.get("issues")
        if isinstance(issues, list):
            actions.extend(_issue_actions(source.name, payload, issues))
    return _dedupe_actions(actions)


def _dedupe_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[object, ...]] = set()
    for action in actions:
        key = (
            action["phase"],
            action["severity"],
            action["source_check"],
            action["target_path"],
            action["minimal_fix"],
            action["blocks_completion"],
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(action)
    return deduped


def _issue_actions(
    source_check: str,
    payload: dict[str, Any],
    issues: list[object],
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        severity = _string_value(issue.get("severity"), "error")
        target_path = _string_value(issue.get("path"), ".")
        message = _string_value(issue.get("message"), f"{source_check} issue")
        phase = _issue_phase(source_check, issue)
        actions.append(
            {
                "phase": phase,
                "severity": severity,
                "source_check": source_check,
                "target_path": target_path,
                "action": "repair_check_issue",
                "minimal_fix": _minimal_fix(source_check, payload, phase, message),
                "blocks_completion": severity == "error",
            }
        )
    return actions


def _issue_phase(source_check: str, issue: dict[str, Any]) -> str:
    if source_check == "methodology-loop":
        code = _string_value(issue.get("code"))
        parts = code.split(".")
        if len(parts) == 2:
            phase = parts[1].rsplit("_", 1)[0]
            if phase in {"orient", "scope", "execute", "prove", "update_knowledge", "handoff"}:
                return phase
    return PHASE_BY_SOURCE_CHECK.get(source_check, "orient")


def _minimal_fix(source_check: str, payload: dict[str, Any], phase: str, message: str) -> str:
    if source_check == "methodology-loop":
        recommended_fix = _phase_recommended_fix(payload, phase)
        if recommended_fix:
            return recommended_fix
    return _strip_message_prefix(source_check, message)


def _phase_recommended_fix(payload: dict[str, Any], phase: str) -> str:
    phases = payload.get("phases")
    if not isinstance(phases, list):
        return ""
    for item in phases:
        if not isinstance(item, dict) or item.get("name") != phase:
            continue
        recommended_fix = item.get("recommended_fix")
        if isinstance(recommended_fix, str):
            return recommended_fix
    return ""


def _strip_message_prefix(source_check: str, message: str) -> str:
    prefix = f"{source_check}: "
    if message.startswith(prefix):
        return message.removeprefix(prefix)
    return message


def _string_value(value: object, default: str = "") -> str:
    return value if isinstance(value, str) else default


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
