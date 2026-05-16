from __future__ import annotations

from pathlib import Path
from typing import Any

from .graph_index import ContractIndex, string_list, task_proof_ids
from .model import ContractDocument
from .report import versioned_report
from .validate import validate_path


def build_graph_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
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
    nodes = [_node(document, report.root) for document in sorted(report.documents, key=lambda item: item.identifier)]
    edges = _dedupe_edges(
        [
            *_goal_edges(index),
            *_task_edges(index),
            *_review_edges(index),
            *_handoff_edges(index),
            *_integration_edges(index),
        ]
    )
    return versioned_report(
        {
            "ok": True,
            "status": "valid",
            "contracts": len(report.documents),
            "nodes": nodes,
            "edges": edges,
        }
    )


def _goal_edges(index: ContractIndex) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for goal in index.goals():
        contracts = goal.data.get("contracts")
        if not isinstance(contracts, dict):
            continue
        source = _key(goal.kind, goal.identifier)
        edges.extend(_edges(source, "goal_has_module", "module_contract", string_list(contracts.get("modules"))))
        edges.extend(_edges(source, "goal_has_task", "task_contract", string_list(contracts.get("tasks"))))
        edges.extend(_edges(source, "goal_requires_proof", "proof_contract", string_list(contracts.get("proofs"))))
        edges.extend(_edges(source, "goal_requires_review", "review_contract", string_list(contracts.get("reviews"))))
        integration = contracts.get("integration")
        if isinstance(integration, str) and integration:
            edges.append(_edge(source, "goal_integrates_with", _key("integration_contract", integration)))
    return edges


def _task_edges(index: ContractIndex) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for task in index.by_kind.get("task_contract", {}).values():
        source = _key(task.kind, task.identifier)
        edges.extend(_edges(source, "task_touches_module", "module_contract", string_list(task.data.get("modules"))))
        edges.extend(_edges(source, "task_requires_proof", "proof_contract", task_proof_ids(task)))
    return edges


def _review_edges(index: ContractIndex) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for review in index.by_kind.get("review_contract", {}).values():
        target = review.data.get("target_task")
        if isinstance(target, str) and target:
            edges.append(_edge(_key(review.kind, review.identifier), "review_targets_task", _key("task_contract", target)))
    return edges


def _handoff_edges(index: ContractIndex) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for handoff in index.by_kind.get("handoff_contract", {}).values():
        task_id = handoff.data.get("task_id")
        if isinstance(task_id, str) and task_id:
            edges.append(_edge(_key(handoff.kind, handoff.identifier), "handoff_for_task", _key("task_contract", task_id)))
    return edges


def _integration_edges(index: ContractIndex) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for integration in index.by_kind.get("integration_contract", {}).values():
        source = _key(integration.kind, integration.identifier)
        edges.extend(_edges(source, "integration_has_task", "task_contract", string_list(integration.data.get("tasks"))))
        edges.extend(
            _edges(
                source,
                "integration_orders_task",
                "task_contract",
                string_list(integration.data.get("merge_order")),
            )
        )
    return edges


def _edges(source: str, relation: str, target_kind: str, targets: list[str]) -> list[dict[str, str]]:
    return [_edge(source, relation, _key(target_kind, target)) for target in targets]


def _edge(source: str, relation: str, target: str) -> dict[str, str]:
    return {
        "source": source,
        "target": target,
        "relation": relation,
    }


def _dedupe_edges(edges: list[dict[str, str]]) -> list[dict[str, str]]:
    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for edge in edges:
        key = (edge["source"], edge["relation"], edge["target"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(edge)
    return deduped


def _node(document: ContractDocument, root: Path) -> dict[str, str]:
    return {
        "key": _key(document.kind, document.identifier),
        "id": document.identifier,
        "kind": document.kind,
        "path": _relative_path(document, root),
    }


def _key(kind: str, identifier: str) -> str:
    return f"{kind}:{identifier}"


def _relative_path(document: ContractDocument, root: Path) -> str:
    try:
        return str(document.path.relative_to(root))
    except ValueError:
        return str(document.path)
