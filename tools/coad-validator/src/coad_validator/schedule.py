from __future__ import annotations

from pathlib import Path
from typing import Any

from .graph_index import ContractIndex, string_list
from .model import ContractDocument
from .report import versioned_report
from .validate import validate_path


def build_schedule_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    report = validate_path(root, schema_dir=schema_dir)
    if not report.ok:
        return versioned_report(
            {
                "ok": False,
                "status": "invalid",
                "contracts": len(report.documents),
                "issues": [issue.to_json(report.root) for issue in report.issues],
            }
        )

    index = ContractIndex.from_documents(report.documents)
    goals = [_goal_schedule(goal, index, report.root) for goal in index.goals()]
    return versioned_report(
        {
            "ok": True,
            "status": "scheduled",
            "contracts": len(report.documents),
            "goals": goals,
        }
    )


def _goal_schedule(goal: ContractDocument, index: ContractIndex, root: Path) -> dict[str, Any]:
    tasks = index.goal_tasks(goal)
    max_parallel_agents = _max_parallel_agents(goal)
    conflicts = _write_scope_conflicts(tasks)
    waves, blocked = _schedule_waves(tasks, index, root, max_parallel_agents)
    return {
        "goal_id": goal.identifier,
        "path": _relative_path(goal, root),
        "max_parallel_agents": max_parallel_agents,
        "waves": waves,
        "blocked": blocked,
        "conflicts": conflicts,
    }


def _schedule_waves(
    tasks: list[ContractDocument],
    index: ContractIndex,
    root: Path,
    max_parallel_agents: int,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    remaining = [task for task in tasks if _task_status(task) != "complete"]
    completed = {task.identifier for task in tasks if _task_status(task) == "complete"}
    waves: list[dict[str, Any]] = []
    blocked: list[dict[str, str]] = []

    while remaining:
        wave_tasks: list[ContractDocument] = []
        next_remaining: list[ContractDocument] = []
        for task in remaining:
            blocker = _dependency_blocker(task, index, completed)
            if blocker is not None:
                next_remaining.append(task)
                continue
            if len(wave_tasks) >= max_parallel_agents or _conflicts_with_any(task, wave_tasks):
                next_remaining.append(task)
                continue
            wave_tasks.append(task)

        if not wave_tasks:
            blocked.extend(_blocked_task(task, root, "dependencies are not schedulable") for task in remaining)
            break

        waves.append(
            {
                "index": len(waves) + 1,
                "tasks": [_task_entry(task, root) for task in wave_tasks],
            }
        )
        completed.update(task.identifier for task in wave_tasks)
        remaining = next_remaining

    return waves, blocked


def _dependency_blocker(
    task: ContractDocument,
    index: ContractIndex,
    completed: set[str],
) -> str | None:
    for dependency in string_list(task.data.get("dependencies")):
        dependency_task = index.task(dependency)
        if dependency_task is None:
            return f"missing dependency task: {dependency}"
        if dependency not in completed:
            return f"dependency not complete: {dependency}"
    return None


def _write_scope_conflicts(tasks: list[ContractDocument]) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    for left_index, left in enumerate(tasks):
        for right in tasks[left_index + 1:]:
            conflict = _first_conflict(left, right)
            if conflict is None:
                continue
            conflicts.append(conflict)
    return conflicts


def _conflicts_with_any(task: ContractDocument, wave_tasks: list[ContractDocument]) -> bool:
    return any(_first_conflict(task, other) for other in wave_tasks)


def _first_conflict(left: ContractDocument, right: ContractDocument) -> dict[str, Any] | None:
    write_overlap = _first_scope_overlap(_write_scope(left), _write_scope(right))
    if write_overlap is not None:
        return _conflict(left, right, "write_scope_overlap", write_overlap)

    left_writes_right_reads = _first_scope_overlap(_write_scope(left), _read_scope(right))
    if left_writes_right_reads is not None:
        return _conflict(left, right, "read_write_overlap", left_writes_right_reads)

    right_writes_left_reads = _first_scope_overlap(_write_scope(right), _read_scope(left))
    if right_writes_left_reads is not None:
        return _conflict(left, right, "read_write_overlap", right_writes_left_reads)
    return None


def _conflict(
    left: ContractDocument,
    right: ContractDocument,
    conflict_type: str,
    scopes: tuple[str, str],
) -> dict[str, Any]:
    return {
        "task_a": left.identifier,
        "task_b": right.identifier,
        "type": conflict_type,
        "scopes": [scopes[0], scopes[1]],
    }


def _first_scope_overlap(left: list[str], right: list[str]) -> tuple[str, str] | None:
    for left_scope in left:
        for right_scope in right:
            if _scopes_overlap(left_scope, right_scope):
                return left_scope, right_scope
    return None


def _scopes_overlap(left: str, right: str) -> bool:
    if left == right:
        return True
    left_prefix = _tree_prefix(left)
    right_prefix = _tree_prefix(right)
    if left_prefix is not None and _scope_contains(left_prefix, right):
        return True
    if right_prefix is not None and _scope_contains(right_prefix, left):
        return True
    return False


def _tree_prefix(scope: str) -> str | None:
    suffix = "/**"
    if not scope.endswith(suffix):
        return None
    return scope.removesuffix(suffix)


def _scope_contains(prefix: str, scope: str) -> bool:
    return scope == prefix or scope.startswith(f"{prefix}/")


def _task_entry(task: ContractDocument, root: Path) -> dict[str, Any]:
    return {
        "task_id": task.identifier,
        "path": _relative_path(task, root),
        "status": _task_status(task),
        "dependencies": string_list(task.data.get("dependencies")),
        "write_scope": _write_scope(task),
    }


def _blocked_task(task: ContractDocument, root: Path, reason: str) -> dict[str, str]:
    return {
        "task_id": task.identifier,
        "path": _relative_path(task, root),
        "reason": reason,
    }


def _write_scope(task: ContractDocument) -> list[str]:
    return string_list(task.data.get("write_scope"))


def _read_scope(task: ContractDocument) -> list[str]:
    return string_list(task.data.get("read_scope"))


def _task_status(task: ContractDocument) -> str:
    status = task.data.get("status")
    return status if isinstance(status, str) and status else "unknown"


def _max_parallel_agents(goal: ContractDocument) -> int:
    policy = goal.data.get("policy")
    if not isinstance(policy, dict):
        return 1
    value = policy.get("max_parallel_agents")
    return value if isinstance(value, int) and value > 0 else 1


def _relative_path(document: ContractDocument, root: Path) -> str:
    try:
        return str(document.path.relative_to(root))
    except ValueError:
        return str(document.path)
