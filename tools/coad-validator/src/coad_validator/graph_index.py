from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .model import ContractDocument

INDEX_KEYS = {
    "goal_contract": "goal_id",
    "module_contract": "module",
    "task_contract": "task_id",
    "proof_contract": "proof_id",
    "review_contract": "review_id",
    "handoff_contract": "task_id",
    "integration_contract": "integration_id",
}


@dataclass(frozen=True)
class ContractIndex:
    by_kind: dict[str, dict[str, ContractDocument]]

    @classmethod
    def from_documents(cls, documents: list[ContractDocument]) -> "ContractIndex":
        by_kind: dict[str, dict[str, ContractDocument]] = defaultdict(dict)
        for document in documents:
            key = INDEX_KEYS.get(document.kind)
            if key is None:
                continue
            value = document.data.get(key)
            if isinstance(value, str) and value:
                by_kind[document.kind][value] = document
        return cls(by_kind=dict(by_kind))

    def goals(self) -> list[ContractDocument]:
        return sorted(self.by_kind.get("goal_contract", {}).values(), key=lambda item: item.identifier)

    def task(self, task_id: str) -> ContractDocument | None:
        return self.by_kind.get("task_contract", {}).get(task_id)

    def goal_tasks(self, goal: ContractDocument) -> list[ContractDocument]:
        task_ids: list[str] = []
        contracts = goal.data.get("contracts")
        if isinstance(contracts, dict):
            task_ids.extend(string_list(contracts.get("tasks")))
        decomposition = goal.data.get("decomposition")
        if isinstance(decomposition, dict):
            task_ids.extend(string_list(decomposition.get("tasks")))
        return self.documents_for_ids("task_contract", task_ids)

    def goal_for_task(self, task_id: str) -> ContractDocument | None:
        for goal in self.by_kind.get("goal_contract", {}).values():
            if any(task.identifier == task_id for task in self.goal_tasks(goal)):
                return goal
        return None

    def integration_for_task(self, task_id: str) -> ContractDocument | None:
        for integration in self.by_kind.get("integration_contract", {}).values():
            if task_id in string_list(integration.data.get("tasks")):
                return integration
            if task_id in string_list(integration.data.get("merge_order")):
                return integration
        return None

    def task_modules(self, task: ContractDocument) -> list[ContractDocument]:
        return self.documents_for_ids("module_contract", string_list(task.data.get("modules")))

    def task_proofs(self, task: ContractDocument) -> list[ContractDocument]:
        return self.documents_for_ids("proof_contract", task_proof_ids(task))

    def reviews_for_task(self, task_id: str) -> list[ContractDocument]:
        return [
            review
            for review in self.by_kind.get("review_contract", {}).values()
            if review.data.get("target_task") == task_id
        ]

    def handoffs_for_task(self, task_id: str) -> list[ContractDocument]:
        return [
            handoff
            for handoff in self.by_kind.get("handoff_contract", {}).values()
            if handoff.data.get("task_id") == task_id
        ]

    def handoff_for_task(self, task_id: str) -> ContractDocument | None:
        return self.by_kind.get("handoff_contract", {}).get(task_id)

    def proof(self, proof_id: str) -> ContractDocument | None:
        return self.by_kind.get("proof_contract", {}).get(proof_id)

    def documents_for_ids(self, kind: str, ids: list[str]) -> list[ContractDocument]:
        documents: list[ContractDocument] = []
        seen: set[str] = set()
        index = self.by_kind.get(kind, {})
        for identifier in ids:
            if identifier in seen:
                continue
            seen.add(identifier)
            document = index.get(identifier)
            if document is not None:
                documents.append(document)
        return documents


def task_proof_ids(task: ContractDocument) -> list[str]:
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


def string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]
