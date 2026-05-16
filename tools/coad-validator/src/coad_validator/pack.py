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


class PackFailure(Exception):
    pass


def build_context_pack(root: Path, task_id: str, schema_dir: Path | None = None) -> dict[str, Any]:
    report = validate_path(root, schema_dir=schema_dir)
    if not report.ok:
        messages = "; ".join(issue.format(report.root) for issue in report.issues)
        raise PackFailure(f"cannot build context pack from invalid contracts: {messages}")

    by_kind = _index_by_kind(report.documents)
    task = by_kind["task_contract"].get(task_id)
    if task is None:
        raise PackFailure(f"task contract not found: {task_id}")

    goal = _goal_for_task(task_id, by_kind["goal_contract"].values())
    if goal is None:
        raise PackFailure(f"goal contract not found for task: {task_id}")

    modules = _documents_for_ids(by_kind["module_contract"], _string_list(task.data.get("modules")))
    proofs = _documents_for_ids(by_kind["proof_contract"], _task_proof_ids(task))
    reviews = [
        review
        for review in by_kind["review_contract"].values()
        if review.data.get("target_task") == task_id
    ]
    handoffs = [
        handoff
        for handoff in by_kind["handoff_contract"].values()
        if handoff.data.get("task_id") == task_id
    ]
    integration = _integration_for_task(task_id, by_kind["integration_contract"].values())
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


def _goal_for_task(task_id: str, goals: object) -> ContractDocument | None:
    for goal in goals:
        if not isinstance(goal, ContractDocument):
            continue
        decomposition = goal.data.get("decomposition")
        contracts = goal.data.get("contracts")
        if isinstance(decomposition, dict) and task_id in _string_list(decomposition.get("tasks")):
            return goal
        if isinstance(contracts, dict) and task_id in _string_list(contracts.get("tasks")):
            return goal
    return None


def _integration_for_task(task_id: str, integrations: object) -> ContractDocument | None:
    for integration in integrations:
        if not isinstance(integration, ContractDocument):
            continue
        if task_id in _string_list(integration.data.get("tasks")):
            return integration
        if task_id in _string_list(integration.data.get("merge_order")):
            return integration
    return None


def _documents_for_ids(
    index: dict[str, ContractDocument], ids: list[str]
) -> list[ContractDocument]:
    documents: list[ContractDocument] = []
    seen: set[str] = set()
    for identifier in ids:
        if identifier in seen:
            continue
        seen.add(identifier)
        document = index.get(identifier)
        if document is not None:
            documents.append(document)
    return documents


def _task_proof_ids(task: ContractDocument) -> list[str]:
    proof = task.data.get("proof")
    if not isinstance(proof, dict):
        return []
    required = proof.get("required")
    if not isinstance(required, list):
        return []
    proof_ids: list[str] = []
    for item in required:
        if not isinstance(item, dict):
            continue
        proof_id = item.get("proof_id")
        if isinstance(proof_id, str) and proof_id:
            proof_ids.append(proof_id)
    return proof_ids


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


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]
