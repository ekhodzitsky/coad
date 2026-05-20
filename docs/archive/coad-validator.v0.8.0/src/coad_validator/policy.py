from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .graph_index import ContractIndex, string_list
from .model import ContractDocument
from .report import versioned_report
from .validate import ValidationReport, validate_path


@dataclass(frozen=True)
class PolicyIssue:
    path: Path
    message: str
    severity: str = "error"

    def to_json(self, root: Path) -> dict[str, str]:
        return {
            "severity": self.severity,
            "path": _relative_path(self.path, root),
            "message": self.message,
        }


def build_policy_report(
    root: Path,
    schema_dir: Path | None = None,
    contract_report: ValidationReport | None = None,
) -> dict[str, Any]:
    report = contract_report or validate_path(root, schema_dir=schema_dir)
    if not report.ok:
        return versioned_report(
            {
                "ok": False,
                "status": "invalid",
                "contracts": len(report.documents),
                "goals": [],
                "issues": [issue.to_json(report.root) for issue in report.issues],
            }
        )

    index = ContractIndex.from_documents(report.documents)
    issues: list[PolicyIssue] = []
    goals = [_goal_policy(goal, index, report.root, issues) for goal in index.goals()]
    return versioned_report(
        {
            "ok": not issues,
            "status": "pass" if not issues else "policy_issues",
            "contracts": len(report.documents),
            "goals": goals,
            "issues": [issue.to_json(report.root) for issue in issues],
        }
    )


def _goal_policy(
    goal: ContractDocument,
    index: ContractIndex,
    root: Path,
    issues: list[PolicyIssue],
) -> dict[str, Any]:
    policy = goal.data.get("policy")
    policy_data = policy if isinstance(policy, dict) else {}
    allow_external_side_effects = policy_data.get("allow_external_side_effects") is True
    require_contract_updates = policy_data.get("require_contract_updates") is True
    tasks = index.goal_tasks(goal)

    for task in tasks:
        _check_external_side_effects(task, goal, allow_external_side_effects, issues)
        _check_contract_update_handoff(task, goal, require_contract_updates, issues)

    return {
        "goal_id": goal.identifier,
        "path": _relative_path(goal.path, root),
        "tasks": [
            {
                "task_id": task.identifier,
                "path": _relative_path(task.path, root),
            }
            for task in tasks
        ],
    }


def _check_external_side_effects(
    task: ContractDocument,
    goal: ContractDocument,
    allow_external_side_effects: bool,
    issues: list[PolicyIssue],
) -> None:
    side_effects = task.data.get("external_side_effects")
    if allow_external_side_effects or not isinstance(side_effects, list) or not side_effects:
        return
    issues.append(
        PolicyIssue(
            task.path,
            f"task {task.identifier} declares external side effects but goal {goal.identifier} disallows them",
        )
    )


def _check_contract_update_handoff(
    task: ContractDocument,
    goal: ContractDocument,
    require_contract_updates: bool,
    issues: list[PolicyIssue],
) -> None:
    if not require_contract_updates:
        return
    handoff = task.data.get("handoff")
    required_fields = []
    if isinstance(handoff, dict):
        required_fields = string_list(handoff.get("required_fields"))
    if "contract_updates" in required_fields:
        return
    issues.append(
        PolicyIssue(
            task.path,
            f"task {task.identifier} handoff must require contract_updates because goal {goal.identifier} requires contract updates",
        )
    )


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
