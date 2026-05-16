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


def build_status_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
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
        _goal_status(goal, by_kind, report.root)
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


def _goal_status(
    goal: ContractDocument,
    by_kind: dict[str, dict[str, ContractDocument]],
    root: Path,
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    declared_status = _string_value(goal.data.get("status"), "unknown")
    if declared_status != "ready":
        blockers.append(_blocker(goal, root, f"goal status is {declared_status}"))

    task_statuses = [
        _task_status(task, by_kind, root)
        for task in _goal_tasks(goal, by_kind["task_contract"])
    ]
    for task_status in task_statuses:
        blockers.extend(task_status["blockers"])

    ready = not blockers
    return {
        "goal_id": goal.identifier,
        "path": _relative_path(goal, root),
        "declared_status": declared_status,
        "ready": ready,
        "status": "ready" if ready else "not_ready",
        "blockers": blockers,
        "tasks": task_statuses,
    }


def _task_status(
    task: ContractDocument,
    by_kind: dict[str, dict[str, ContractDocument]],
    root: Path,
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    task_id = task.identifier
    declared_status = _string_value(task.data.get("status"), "unknown")
    if declared_status != "complete":
        blockers.append(_blocker(task, root, f"task {task_id} status is {declared_status}"))

    handoff = by_kind["handoff_contract"].get(task_id)
    if handoff is None:
        blockers.append(_blocker(task, root, f"task {task_id} has no handoff"))
    else:
        handoff_status = _string_value(handoff.data.get("status"), "unknown")
        if handoff_status != "complete":
            blockers.append(_blocker(handoff, root, f"task {task_id} handoff status is {handoff_status}"))
        blockers.extend(_proof_blockers(task, handoff, root))

    ready = not blockers
    return {
        "task_id": task_id,
        "path": _relative_path(task, root),
        "declared_status": declared_status,
        "ready": ready,
        "status": "ready" if ready else "not_ready",
        "blockers": blockers,
    }


def _proof_blockers(
    task: ContractDocument,
    handoff: ContractDocument,
    root: Path,
) -> list[dict[str, str]]:
    passing_commands = set(_passing_handoff_commands(handoff))
    blockers: list[dict[str, str]] = []
    for command in _required_task_commands(task):
        if command not in passing_commands:
            blockers.append(
                _blocker(
                    handoff,
                    root,
                    f"task {task.identifier} proof command is not passing: {command}",
                )
            )
    return blockers


def _required_task_commands(task: ContractDocument) -> list[str]:
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


def _passing_handoff_commands(handoff: ContractDocument) -> list[str]:
    proof_results = handoff.data.get("proof_results")
    if not isinstance(proof_results, list):
        return []
    commands: list[str] = []
    for item in proof_results:
        if not isinstance(item, dict):
            continue
        command = item.get("command")
        status = item.get("status")
        if isinstance(command, str) and status == "pass":
            commands.append(command)
    return commands


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
