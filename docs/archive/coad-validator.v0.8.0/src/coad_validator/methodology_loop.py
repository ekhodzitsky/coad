from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .agent_guidance import build_agent_guidance_report
from .contract_update_integrity import build_contract_update_integrity_report
from .graph_index import ContractIndex, string_list
from .handoff_integrity import build_handoff_integrity_report
from .ledger_handoff_integrity import build_ledger_handoff_integrity_report
from .proof_artifact_integrity import build_proof_artifact_integrity_report
from .proof_result_integrity import build_proof_result_integrity_report
from .report import versioned_report
from .task_scope_integrity import build_task_scope_integrity_report
from .validate import validate_path

if TYPE_CHECKING:
    from .model import ContractDocument
    from .validate import ValidationReport

PHASE_NAMES = ("orient", "scope", "execute", "prove", "update_knowledge", "handoff")
METHODOLOGY_OR_EVIDENCE_SCOPES = {
    "AGENTS.md",
    "CHANGELOG.md",
    "EXECUTION_LEDGER.json",
    "GOAL_CONTRACT.md",
    "HANDOFF.md",
    "INTEGRATION.md",
    "MODULE_CONTRACT.md",
    "PROOF.md",
    "README.md",
    "REVIEW.md",
    "TASK_CONTRACT.md",
    "TODO.md",
    "VERSION",
}


@dataclass(frozen=True)
class Phase:
    name: str
    status: str
    summary: str
    evidence: list[str]
    issues: list[dict[str, str]]
    source_reports: list[str]


def build_methodology_loop_report(
    root: Path,
    schema_dir: Path | None = None,
    contract_report: ValidationReport | None = None,
) -> dict[str, Any]:
    resolved_root = root.resolve()
    report = contract_report or validate_path(resolved_root, schema_dir=schema_dir)
    index = ContractIndex.from_documents(report.documents)
    active_context = _has_active_execution_context(resolved_root)

    phases = [_orient_phase(resolved_root, schema_dir, report)]
    if active_context:
        source_payloads = _source_payloads(resolved_root, schema_dir, report)
        phases.extend(
            [
                _scope_phase(resolved_root, index),
                _execute_phase(source_payloads),
                _prove_phase(source_payloads),
                _update_knowledge_phase(source_payloads),
                _handoff_phase(resolved_root, index),
            ]
        )
    else:
        phases.extend(_skipped_execution_phases())

    status = _overall_status(phases, active_context)
    return versioned_report(
        {
            "claim": "methodology_evidence",
            "limitations": [
                "Checks workflow evidence, not agent intent.",
                "Does not prove semantic code correctness beyond declared proof.",
                "Reports weak or unknown when obligations cannot be inferred mechanically.",
            ],
            "ok": status != "missing",
            "status": status,
            "phases": [_phase_payload(phase) for phase in phases],
            "skip_reason": "no_active_execution_context" if status == "skipped" else "",
            "issues": [issue for phase in phases for issue in phase.issues],
        }
    )


def _source_payloads(root: Path, schema_dir: Path | None, report: ValidationReport) -> dict[str, dict[str, Any]]:
    return {
        "handoff-integrity": build_handoff_integrity_report(root, schema_dir, report),
        "task-scope-integrity": build_task_scope_integrity_report(root, schema_dir, report),
        "ledger-handoff-integrity": build_ledger_handoff_integrity_report(root, schema_dir, report),
        "proof-result-integrity": build_proof_result_integrity_report(root, schema_dir, report),
        "proof-artifact-integrity": build_proof_artifact_integrity_report(root, schema_dir, report),
        "contract-update-integrity": build_contract_update_integrity_report(root, schema_dir, report),
    }


def _orient_phase(root: Path, schema_dir: Path | None, report: ValidationReport) -> Phase:
    agent_guidance = build_agent_guidance_report(root, schema_dir)
    issues: list[dict[str, str]] = []
    if agent_guidance.get("ok") is not True:
        issues.append(_phase_issue("orient", "missing", "AGENTS.md", "agent guidance is missing or invalid"))
    for issue in report.issues:
        issues.append(
            _phase_issue(
                "orient",
                "missing" if issue.severity == "error" else "weak",
                issue.relative_path(root),
                issue.message,
                issue.severity,
            )
        )
    modules = [document for document in report.documents if document.kind == "module_contract"]
    status = _phase_status(issues)
    return Phase(
        "orient",
        status,
        "COAD navigation is available" if status == "pass" else "COAD navigation has gaps",
        [f"module_contracts={len(modules)}", f"validation_ok={report.ok}"],
        issues,
        ["agent-guidance", "validation-report"],
    )


def _scope_phase(root: Path, index: ContractIndex) -> Phase:
    tasks = sorted(index.by_kind.get("task_contract", {}).values(), key=lambda document: document.identifier)
    if not tasks:
        return Phase(
            "scope",
            "missing",
            "No task contract defines the work scope",
            [],
            [_phase_issue("scope", "missing", "TASK_CONTRACT.md", "no task contracts found")],
            ["task-contracts", "module-contracts"],
        )

    issues: list[dict[str, str]] = []
    for task in tasks:
        task_id = task.identifier
        modules = string_list(task.data.get("modules"))
        write_scope = string_list(task.data.get("write_scope"))
        forbidden_mutations = task.data.get("forbidden_mutations")
        required_commands = _required_commands(task)
        path = _relative_path(task.path, root)
        if not modules:
            issues.append(_phase_issue("scope", "missing", path, f"task {task_id} does not declare modules"))
        if not write_scope:
            issues.append(_phase_issue("scope", "missing", path, f"task {task_id} does not declare write_scope"))
        if not isinstance(forbidden_mutations, list):
            issues.append(_phase_issue("scope", "missing", path, f"task {task_id} does not declare forbidden_mutations"))
        if not required_commands:
            issues.append(_phase_issue("scope", "missing", path, f"task {task_id} does not declare required proof commands"))
        module_documents = index.task_modules(task)
        if len(module_documents) != len(set(modules)):
            issues.append(_phase_issue("scope", "missing", path, f"task {task_id} references unknown target modules"))
        for scope in _unowned_write_scopes(write_scope, module_documents):
            issues.append(
                _phase_issue(
                    "scope",
                    "weak",
                    path,
                    f"task {task_id} write_scope is not covered by target module ownership: {scope}",
                    severity="warning",
                )
            )
    status = _phase_status(issues)
    return Phase(
        "scope",
        status,
        "Task scope is bound to modules and proof" if status == "pass" else "Task scope has gaps",
        [f"task_contracts={len(tasks)}"],
        issues,
        ["task-contracts", "module-contracts"],
    )


def _execute_phase(source_payloads: dict[str, dict[str, Any]]) -> Phase:
    return _aggregate_phase(
        "execute",
        [
            ("handoff-integrity", source_payloads["handoff-integrity"]),
            ("ledger-handoff-integrity", source_payloads["ledger-handoff-integrity"]),
            ("task-scope-integrity", source_payloads["task-scope-integrity"]),
        ],
        "Changed files are tied to handoff, ledger, and task scope",
    )


def _prove_phase(source_payloads: dict[str, dict[str, Any]]) -> Phase:
    return _aggregate_phase(
        "prove",
        [
            ("proof-result-integrity", source_payloads["proof-result-integrity"]),
            ("proof-artifact-integrity", source_payloads["proof-artifact-integrity"]),
        ],
        "Required proof is passing and artifact-backed",
    )


def _update_knowledge_phase(source_payloads: dict[str, dict[str, Any]]) -> Phase:
    payload = source_payloads["contract-update-integrity"]
    status = _payload_phase_status(payload, warning_is_weak=True, skipped_is_unknown=True)
    issues = _source_phase_issues("update_knowledge", payload, status)
    return Phase(
        "update_knowledge",
        status,
        "Knowledge updates are declared" if status == "pass" else "Knowledge update evidence is incomplete",
        [_source_evidence("contract-update-integrity", payload)],
        issues,
        ["contract-update-integrity"],
    )


def _handoff_phase(root: Path, index: ContractIndex) -> Phase:
    handoffs = sorted(index.by_kind.get("handoff_contract", {}).values(), key=lambda document: document.identifier)
    if not handoffs:
        return Phase(
            "handoff",
            "missing",
            "No handoff contract closes the work",
            [],
            [_phase_issue("handoff", "missing", "HANDOFF.md", "no handoff contracts found")],
            ["handoff-contracts"],
        )

    issues: list[dict[str, str]] = []
    for handoff in handoffs:
        path = _relative_path(handoff.path, root)
        status = _string_value(handoff.data.get("status"))
        changed_files = _list_value(handoff.data.get("changed_files"))
        proof_results = _list_value(handoff.data.get("proof_results"))
        known_gaps = _list_value(handoff.data.get("known_gaps"))
        follow_up_tasks = _list_value(handoff.data.get("follow_up_tasks"))
        if not changed_files:
            issues.append(_phase_issue("handoff", "missing", path, "handoff does not declare changed_files"))
        if not proof_results:
            issues.append(_phase_issue("handoff", "missing", path, "handoff does not declare proof_results"))
        if status == "complete":
            continue
        if not known_gaps:
            issues.append(
                _phase_issue(
                    "handoff",
                    "missing",
                    path,
                    "incomplete handoff must declare known_gaps",
                )
            )
        if not follow_up_tasks:
            issues.append(
                _phase_issue(
                    "handoff",
                    "missing",
                    path,
                    "incomplete handoff must declare follow_up_tasks",
                )
            )
    phase_status = _phase_status(issues)
    return Phase(
        "handoff",
        phase_status,
        "Handoff is complete and reviewable" if phase_status == "pass" else "Handoff closure has gaps",
        [f"handoffs={len(handoffs)}"],
        issues,
        ["handoff-contracts"],
    )


def _aggregate_phase(name: str, sources: list[tuple[str, dict[str, Any]]], pass_summary: str) -> Phase:
    status = "pass"
    evidence: list[str] = []
    issues: list[dict[str, str]] = []
    for source_name, payload in sources:
        source_status = _payload_phase_status(payload, warning_is_weak=True, skipped_is_unknown=True)
        evidence.append(_source_evidence(source_name, payload))
        if _status_rank(source_status) > _status_rank(status):
            status = source_status
        issues.extend(_source_phase_issues(name, payload, source_status))
    return Phase(
        name,
        status,
        pass_summary if status == "pass" else f"{name.replace('_', ' ')} phase is incomplete",
        evidence,
        issues,
        [source_name for source_name, _payload in sources],
    )


def _payload_phase_status(payload: dict[str, Any], *, warning_is_weak: bool, skipped_is_unknown: bool) -> str:
    status = _string_value(payload.get("status"))
    if payload.get("ok") is not True:
        return "missing"
    if status == "warning" and warning_is_weak:
        return "weak"
    if status == "skipped" and skipped_is_unknown:
        return "unknown"
    return "pass"


def _source_phase_issues(phase: str, payload: dict[str, Any], status: str) -> list[dict[str, str]]:
    if status == "pass":
        return []
    severity = "warning" if status == "weak" else "info" if status == "unknown" else "error"
    source_status = _string_value(payload.get("status"), "unknown")
    return [
        _phase_issue(
            phase,
            status,
            _issue_path(payload),
            f"{_source_label(payload)} reported {source_status}",
            severity=severity,
        )
    ]


def _skipped_execution_phases() -> list[Phase]:
    return [
        Phase(name, "skipped", "No active execution context in this root", ["execution-context"], [], ["execution-context"])
        for name in PHASE_NAMES
        if name != "orient"
    ]


def _overall_status(phases: list[Phase], active_context: bool) -> str:
    if any(phase.status == "missing" for phase in phases):
        return "missing"
    if not active_context:
        return "skipped"
    if any(phase.status == "weak" for phase in phases):
        return "partial"
    if any(phase.status == "unknown" for phase in phases):
        return "unknown"
    return "pass"


def _phase_status(issues: list[dict[str, str]]) -> str:
    if any(issue["severity"] == "error" for issue in issues):
        return "missing"
    if issues:
        return "weak"
    return "pass"


def _phase_payload(phase: Phase) -> dict[str, Any]:
    return {
        "name": phase.name,
        "status": phase.status,
        "summary": phase.summary,
        "evidence": phase.evidence,
        "source_reports": phase.source_reports,
        "blocking_issues": _blocking_issues(phase),
        "recommended_fix": _recommended_fix(phase),
        "issues": phase.issues,
    }


def _blocking_issues(phase: Phase) -> list[str]:
    return [
        _strip_phase_prefix(issue["message"])
        for issue in phase.issues
        if issue.get("severity") == "error"
    ]


def _strip_phase_prefix(message: str) -> str:
    marker = ": "
    if marker in message:
        return message.split(marker, 1)[1]
    return message


def _recommended_fix(phase: Phase) -> str:
    if phase.status == "pass":
        return "No action needed."
    if phase.status == "skipped":
        return "Start an execution context with HANDOFF.md or EXECUTION_LEDGER.json when full loop validation is needed."
    return {
        "orient": (
            "Fix AGENTS.md, module contracts, README/TODO context files, "
            "workcell ownership, and context budgets until validation passes."
        ),
        "scope": (
            "Add or fix TASK_CONTRACT.md with target modules, write_scope, "
            "forbidden_mutations, and required proof commands."
        ),
        "execute": (
            "Align HANDOFF.changed_files, EXECUTION_LEDGER changed_files/task_id, "
            "and task write_scope with the real Git diff."
        ),
        "prove": (
            "Record every required proof command as pass in HANDOFF and ledger, "
            "then attach non-empty digest-checked proof artifacts."
        ),
        "update_knowledge": (
            "Record changed contracts, schemas, methodology docs, public surfaces, "
            "ownership, and known gaps in contract_updates or module docs."
        ),
        "handoff": (
            "Close HANDOFF.md with status, changed_files, proof_results, and "
            "known_gaps plus follow_up_tasks when the work is incomplete."
        ),
    }[phase.name]


def _phase_issue(
    phase: str,
    status: str,
    path: str,
    message: str,
    severity: str = "error",
) -> dict[str, str]:
    return {
        "code": f"methodology_loop.{phase}_{status}",
        "severity": severity,
        "path": path,
        "message": f"{phase.replace('_', ' ')} phase is {status}: {message}",
    }


def _required_commands(task: ContractDocument) -> list[str]:
    proof = task.data.get("proof")
    if not isinstance(proof, dict):
        return []
    required = proof.get("required")
    if not isinstance(required, list):
        return []
    commands: list[str] = []
    for item in required:
        if not isinstance(item, dict):
            continue
        command = item.get("command")
        if isinstance(command, str) and command:
            commands.append(command)
    return commands


def _unowned_write_scopes(write_scope: list[str], modules: list[ContractDocument]) -> list[str]:
    owned_prefixes = [
        _scope_prefix(scope)
        for module in modules
        for scope in _module_owns_paths(module)
    ]
    return [
        scope
        for scope in write_scope
        if not _is_methodology_or_evidence_scope(scope)
        and not any(_scope_prefix(scope).startswith(owned_prefix) for owned_prefix in owned_prefixes if owned_prefix)
    ]


def _module_owns_paths(module: ContractDocument) -> list[str]:
    workcell = module.data.get("workcell")
    if not isinstance(workcell, dict):
        return []
    return string_list(workcell.get("owns_paths"))


def _scope_prefix(scope: str) -> str:
    value = scope.removesuffix("/**").rstrip("/")
    return value or scope


def _is_methodology_or_evidence_scope(scope: str) -> bool:
    prefix = _scope_prefix(scope)
    if prefix in METHODOLOGY_OR_EVIDENCE_SCOPES:
        return True
    return prefix.startswith(("artifacts", "contracts", "docs", "schema", "project-contracts"))


def _has_active_execution_context(root: Path) -> bool:
    return (root / "HANDOFF.md").is_file() or (root / "EXECUTION_LEDGER.json").is_file()


def _source_evidence(source_name: str, payload: dict[str, Any]) -> str:
    return f"{source_name}:{_string_value(payload.get('status'), 'unknown')}"


def _source_label(payload: dict[str, Any]) -> str:
    if "task_id" in payload:
        return "task scope"
    if "changed_methodology_files" in payload:
        return "contract update integrity"
    if "artifacts" in payload:
        return "proof artifact integrity"
    if "required_commands" in payload:
        return "proof result integrity"
    if "entries" in payload:
        return "ledger handoff integrity"
    return "source report"


def _issue_path(payload: dict[str, Any]) -> str:
    issues = payload.get("issues")
    if isinstance(issues, list):
        for issue in issues:
            if isinstance(issue, dict):
                path = issue.get("path")
                if isinstance(path, str):
                    return path
    return "."


def _status_rank(status: str) -> int:
    return {"pass": 0, "skipped": 1, "unknown": 2, "weak": 3, "missing": 4}.get(status, 4)


def _list_value(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _string_value(value: object, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
