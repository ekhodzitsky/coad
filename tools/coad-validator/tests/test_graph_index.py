from __future__ import annotations

from pathlib import Path

from coad_validator.graph_index import ContractIndex
from coad_validator.validate import validate_path

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
FIXTURES = Path(__file__).parent / "fixtures"


def test_contract_index_resolves_task_graph_neighbors() -> None:
    report = validate_path(FIXTURES / "valid" / "minimal-graph", schema_dir=SCHEMA_DIR)
    index = ContractIndex.from_documents(report.documents)

    task = index.task("checkout-negative-total-guard")

    assert task is not None
    goal = index.goal_for_task(task.identifier)
    integration = index.integration_for_task(task.identifier)
    assert goal is not None
    assert integration is not None
    assert goal.identifier == "checkout-negative-total-hardening"
    assert integration.identifier == "checkout-negative-total-integration"
    assert [module.identifier for module in index.task_modules(task)] == ["checkout"]
    assert [proof.identifier for proof in index.task_proofs(task)] == ["checkout-negative-total-proof"]
    assert [review.identifier for review in index.reviews_for_task(task.identifier)] == [
        "checkout-negative-total-review"
    ]
    assert [handoff.identifier for handoff in index.handoffs_for_task(task.identifier)] == [
        "checkout-negative-total-guard"
    ]


def test_contract_index_deduplicates_goal_task_references() -> None:
    report = validate_path(FIXTURES / "valid" / "minimal-graph", schema_dir=SCHEMA_DIR)
    index = ContractIndex.from_documents(report.documents)
    goal = index.goals()[0]

    assert [task.identifier for task in index.goal_tasks(goal)] == [
        "checkout-negative-total-guard"
    ]
