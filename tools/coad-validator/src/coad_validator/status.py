from __future__ import annotations

from pathlib import Path
from typing import Any

from .graph_index import ContractIndex
from .model import ContractDocument
from .report import versioned_report
from .validate import validate_path


def build_status_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    report = validate_path(root, schema_dir=schema_dir)
    if not report.ok:
        return versioned_report(
            {
                "ok": False,
                "ready": False,
                "status": "invalid",
                "contracts": len(report.documents),
                "issues": [issue.to_json(report.root) for issue in report.issues],
            }
        )

    index = ContractIndex.from_documents(report.documents)
    goals = [
        _goal_status(goal, index, report.root)
        for goal in index.goals()
    ]
    ready = bool(goals) and all(goal["ready"] for goal in goals)
    return versioned_report(
        {
            "ok": True,
            "ready": ready,
            "status": "ready" if ready else "not_ready",
            "contracts": len(report.documents),
            "goals": goals,
        }
    )


def _goal_status(
    goal: ContractDocument,
    index: ContractIndex,
    root: Path,
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    declared_status = _string_value(goal.data.get("status"), "unknown")
    if declared_status != "ready":
        blockers.append(_blocker(goal, root, f"goal status is {declared_status}"))

    task_statuses = [
        _task_status(task, index, root)
        for task in index.goal_tasks(goal)
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
    index: ContractIndex,
    root: Path,
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    task_id = task.identifier
    declared_status = _string_value(task.data.get("status"), "unknown")
    if declared_status != "complete":
        blockers.append(_blocker(task, root, f"task {task_id} status is {declared_status}"))

    handoff = index.handoff_for_task(task_id)
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


def _string_value(value: object, fallback: str) -> str:
    return value if isinstance(value, str) and value else fallback
