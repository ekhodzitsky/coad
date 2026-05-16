from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .model import ContractDocument
from .validate import validate_path

_INDEX_KEYS = {
    "goal_contract": "goal_id",
    "module_contract": "module",
    "task_contract": "task_id",
    "proof_contract": "proof_id",
    "review_contract": "review_id",
    "handoff_contract": "task_id",
    "integration_contract": "integration_id",
}


def build_proof_matrix(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    report = validate_path(root, schema_dir=schema_dir)
    if not report.ok:
        return {
            "ok": False,
            "ready": False,
            "status": "invalid",
            "contracts": len(report.documents),
            "issues": [issue.to_json(report.root) for issue in report.issues],
        }

    by_kind = _index_by_kind(report.documents)
    goals = [
        _goal_matrix(goal, by_kind, report.root)
        for goal in sorted(by_kind["goal_contract"].values(), key=lambda item: item.identifier)
    ]
    ready = bool(goals) and all(goal["ready"] for goal in goals)
    return {
        "ok": True,
        "ready": ready,
        "status": "ready" if ready else "not_ready",
        "contracts": len(report.documents),
        "goals": goals,
    }


def _goal_matrix(
    goal: ContractDocument,
    by_kind: dict[str, dict[str, ContractDocument]],
    root: Path,
) -> dict[str, Any]:
    tasks = [_task_matrix(task, by_kind, root) for task in _goal_tasks(goal, by_kind["task_contract"])]
    blockers = [blocker for task in tasks for blocker in task["blockers"]]
    ready = not blockers
    return {
        "goal_id": goal.identifier,
        "path": _relative_path(goal, root),
        "ready": ready,
        "status": "ready" if ready else "not_ready",
        "blockers": blockers,
        "tasks": tasks,
    }


def _task_matrix(
    task: ContractDocument,
    by_kind: dict[str, dict[str, ContractDocument]],
    root: Path,
) -> dict[str, Any]:
    task_id = task.identifier
    handoff = by_kind["handoff_contract"].get(task_id)
    proofs = [
        _proof_entry(task, required, handoff, by_kind["proof_contract"], root)
        for required in _required_task_proofs(task)
    ]
    blockers = [
        _blocker(task, root, f"task {task_id} missing passing evidence for proof command: {proof['command']}")
        for proof in proofs
        if proof["status"] != "pass"
    ]
    ready = not blockers
    return {
        "task_id": task_id,
        "path": _relative_path(task, root),
        "change_class": _string_value(task.data.get("change_class"), "unknown"),
        "ready": ready,
        "status": "ready" if ready else "not_ready",
        "blockers": blockers,
        "proofs": proofs,
    }


def _proof_entry(
    task: ContractDocument,
    required: dict[str, Any],
    handoff: ContractDocument | None,
    proof_index: dict[str, ContractDocument],
    root: Path,
) -> dict[str, Any]:
    proof_id = _string_value(required.get("proof_id"), "")
    command = _string_value(required.get("command"), "")
    proof_contract = proof_index.get(proof_id)
    evidence = _handoff_evidence(command, handoff, root)
    status = "pass" if evidence is not None and evidence["status"] == "pass" else "missing_evidence"
    return {
        "proof_id": proof_id,
        "command": command,
        "kind": _string_value(required.get("kind"), "unknown"),
        "target": _string_value(required.get("target"), ""),
        "proof_contract": _contract_ref(proof_contract, root),
        "evidence": evidence,
        "status": status,
    }


def _handoff_evidence(
    command: str,
    handoff: ContractDocument | None,
    root: Path,
) -> dict[str, str] | None:
    if handoff is None:
        return None
    proof_results = handoff.data.get("proof_results")
    if not isinstance(proof_results, list):
        return None
    for item in proof_results:
        if not isinstance(item, dict):
            continue
        if item.get("command") != command:
            continue
        status = item.get("status")
        return {
            "status": status if isinstance(status, str) else "unknown",
            "source": _relative_path(handoff, root),
        }
    return None


def _required_task_proofs(task: ContractDocument) -> list[dict[str, Any]]:
    proof = task.data.get("proof")
    if not isinstance(proof, dict):
        return []
    required = proof.get("required")
    if not isinstance(required, list):
        return []
    return [item for item in required if isinstance(item, dict)]


def _goal_tasks(
    goal: ContractDocument,
    task_index: dict[str, ContractDocument],
) -> list[ContractDocument]:
    task_ids: list[str] = []
    contracts = goal.data.get("contracts")
    if isinstance(contracts, dict):
        task_ids.extend(_string_list(contracts.get("tasks")))
    decomposition = goal.data.get("decomposition")
    if isinstance(decomposition, dict):
        task_ids.extend(_string_list(decomposition.get("tasks")))

    tasks: list[ContractDocument] = []
    seen: set[str] = set()
    for task_id in task_ids:
        if task_id in seen:
            continue
        seen.add(task_id)
        task = task_index.get(task_id)
        if task is not None:
            tasks.append(task)
    return tasks


def _index_by_kind(documents: list[ContractDocument]) -> dict[str, dict[str, ContractDocument]]:
    by_kind: dict[str, dict[str, ContractDocument]] = defaultdict(dict)
    for document in documents:
        key = _INDEX_KEYS.get(document.kind)
        if key is None:
            continue
        value = document.data.get(key)
        if isinstance(value, str) and value:
            by_kind[document.kind][value] = document
    return by_kind


def _contract_ref(document: ContractDocument | None, root: Path) -> dict[str, str] | None:
    if document is None:
        return None
    return {
        "id": document.identifier,
        "path": _relative_path(document, root),
    }


def _blocker(document: ContractDocument, root: Path, message: str) -> dict[str, str]:
    return {
        "kind": document.kind,
        "id": document.identifier,
        "path": _relative_path(document, root),
        "message": message,
    }


def _relative_path(document: ContractDocument, root: Path) -> str:
    try:
        return str(document.path.relative_to(root))
    except ValueError:
        return str(document.path)


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _string_value(value: object, fallback: str) -> str:
    return value if isinstance(value, str) and value else fallback
