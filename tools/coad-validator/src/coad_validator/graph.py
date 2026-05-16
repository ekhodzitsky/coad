from __future__ import annotations

from collections import defaultdict

from .model import ContractDocument, ValidationIssue
from .schema import document_issue

_INDEX_KEYS = {
    "goal_contract": "goal_id",
    "module_contract": "module",
    "task_contract": "task_id",
    "proof_contract": "proof_id",
    "review_contract": "review_id",
    "integration_contract": "integration_id",
}


def validate_graph(documents: list[ContractDocument]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    by_kind = _index_by_kind(documents, issues)

    for goal in by_kind.get("goal_contract", {}).values():
        issues.extend(_validate_goal(goal, by_kind))

    for task in by_kind.get("task_contract", {}).values():
        issues.extend(_validate_task(task, by_kind))

    for review in by_kind.get("review_contract", {}).values():
        issues.extend(_validate_review(review, by_kind))

    for handoff in by_kind.get("handoff_contract", {}).values():
        issues.extend(_validate_handoff(handoff, by_kind))

    for integration in by_kind.get("integration_contract", {}).values():
        issues.extend(_validate_integration(integration, by_kind))

    return issues


def _index_by_kind(
    documents: list[ContractDocument], issues: list[ValidationIssue]
) -> dict[str, dict[str, ContractDocument]]:
    by_kind: dict[str, dict[str, ContractDocument]] = defaultdict(dict)
    for document in documents:
        key_name = _INDEX_KEYS.get(document.kind)
        if key_name is None:
            continue
        value = document.data.get(key_name)
        if not isinstance(value, str) or not value:
            continue
        existing = by_kind[document.kind].get(value)
        if existing is not None:
            issues.append(document_issue(document, f"duplicate {key_name}: {value}"))
            issues.append(document_issue(existing, f"duplicate {key_name}: {value}"))
            continue
        by_kind[document.kind][value] = document
    return by_kind


def _validate_goal(
    goal: ContractDocument, by_kind: dict[str, dict[str, ContractDocument]]
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    contracts = goal.data.get("contracts", {})
    if isinstance(contracts, dict):
        issues.extend(
            _missing_refs(goal, "module", contracts.get("modules", []), by_kind["module_contract"])
        )
        issues.extend(
            _missing_refs(goal, "task", contracts.get("tasks", []), by_kind["task_contract"])
        )
        issues.extend(
            _missing_refs(goal, "proof", contracts.get("proofs", []), by_kind["proof_contract"])
        )
        issues.extend(
            _missing_refs(goal, "review", contracts.get("reviews", []), by_kind["review_contract"])
        )
        integration = contracts.get("integration")
        if isinstance(integration, str) and integration not in by_kind["integration_contract"]:
            issues.append(document_issue(goal, f"missing integration contract: {integration}"))

    oracle = goal.data.get("readiness_oracle", {})
    if isinstance(oracle, dict):
        issues.extend(
            _missing_refs(
                goal,
                "readiness proof",
                oracle.get("required_proof", []),
                by_kind["proof_contract"],
            )
        )

    decomposition = goal.data.get("decomposition", {})
    if isinstance(decomposition, dict):
        issues.extend(
            _missing_refs(
                goal,
                "decomposition task",
                decomposition.get("tasks", []),
                by_kind["task_contract"],
            )
        )
    return issues


def _validate_task(
    task: ContractDocument, by_kind: dict[str, dict[str, ContractDocument]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(_missing_refs(task, "module", task.data.get("modules", []), by_kind["module_contract"]))
    for proof in _task_required_proofs(task):
        if proof not in by_kind["proof_contract"]:
            issues.append(document_issue(task, f"missing proof contract for required proof target: {proof}"))
    return issues


def _validate_review(
    review: ContractDocument, by_kind: dict[str, dict[str, ContractDocument]]) -> list[ValidationIssue]:
    target = review.data.get("target_task")
    if isinstance(target, str) and target not in by_kind["task_contract"]:
        return [document_issue(review, f"missing target task contract: {target}")]
    return []


def _validate_handoff(
    handoff: ContractDocument, by_kind: dict[str, dict[str, ContractDocument]]) -> list[ValidationIssue]:
    task_id = handoff.data.get("task_id")
    if isinstance(task_id, str) and task_id not in by_kind["task_contract"]:
        return [document_issue(handoff, f"missing handoff task contract: {task_id}")]
    return []


def _validate_integration(
    integration: ContractDocument, by_kind: dict[str, dict[str, ContractDocument]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(_missing_refs(integration, "task", integration.data.get("tasks", []), by_kind["task_contract"]))
    issues.extend(
        _missing_refs(
            integration,
            "merge_order task",
            integration.data.get("merge_order", []),
            by_kind["task_contract"],
        )
    )
    return issues


def _missing_refs(
    document: ContractDocument,
    label: str,
    values: object,
    index: dict[str, ContractDocument],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(values, list):
        return issues
    for value in values:
        if isinstance(value, str) and value not in index:
            issues.append(document_issue(document, f"missing {label} contract: {value}"))
    return issues


def _task_required_proofs(task: ContractDocument) -> list[str]:
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
        if isinstance(proof_id, str):
            proof_ids.append(proof_id)
    return proof_ids
