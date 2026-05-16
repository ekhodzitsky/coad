from __future__ import annotations

from pathlib import Path
from typing import Any

from .graph_index import ContractIndex
from .model import ContractDocument
from .validate import validate_path


class PackFailure(Exception):
    pass


def build_context_pack(root: Path, task_id: str, schema_dir: Path | None = None) -> dict[str, Any]:
    report = validate_path(root, schema_dir=schema_dir)
    if not report.ok:
        messages = "; ".join(issue.format(report.root) for issue in report.issues)
        raise PackFailure(f"cannot build context pack from invalid contracts: {messages}")

    index = ContractIndex.from_documents(report.documents)
    task = index.task(task_id)
    if task is None:
        raise PackFailure(f"task contract not found: {task_id}")

    goal = index.goal_for_task(task_id)
    if goal is None:
        raise PackFailure(f"goal contract not found for task: {task_id}")

    modules = index.task_modules(task)
    proofs = index.task_proofs(task)
    reviews = index.reviews_for_task(task_id)
    handoffs = index.handoffs_for_task(task_id)
    integration = index.integration_for_task(task_id)
    if integration is None:
        raise PackFailure(f"integration contract not found for task: {task_id}")

    ordered = [goal, task, *modules, *proofs, *reviews, *handoffs, integration]
    return {
        "task_id": task_id,
        "goal": _contract_payload(goal, report.root),
        "task": _contract_payload(task, report.root),
        "modules": [_contract_payload(document, report.root) for document in modules],
        "proofs": [_contract_payload(document, report.root) for document in proofs],
        "reviews": [_contract_payload(document, report.root) for document in reviews],
        "handoffs": [_contract_payload(document, report.root) for document in handoffs],
        "integration": _contract_payload(integration, report.root),
        "contracts": [_relative_path(document, report.root) for document in ordered],
    }


def _contract_payload(document: ContractDocument, root: Path) -> dict[str, Any]:
    return {
        "id": document.identifier,
        "kind": document.kind,
        "path": _relative_path(document, root),
        "data": document.data,
    }


def _relative_path(document: ContractDocument, root: Path) -> str:
    try:
        return str(document.path.relative_to(root))
    except ValueError:
        return str(document.path)
