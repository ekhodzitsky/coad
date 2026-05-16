from __future__ import annotations

import shutil
from pathlib import Path

from coad_validator.validate import validate_path

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"


def test_minimal_example_validates() -> None:
    report = validate_path(ROOT / "examples" / "minimal", schema_dir=SCHEMA_DIR)

    assert report.ok, [issue.format(report.root) for issue in report.issues]
    assert len(report.documents) == 7


def test_schema_validation_reports_missing_required_field(tmp_path: Path) -> None:
    contract = tmp_path / "GOAL_CONTRACT.md"
    contract.write_text(
        """---
schema_version: 1
kind: goal_contract
goal_id: missing-objective
status: proposed
risk: medium
goal_class: bugfix
terminal_states: [ready]
policy:
  delivery: local
  max_parallel_agents: 1
  allow_external_side_effects: false
  require_contract_updates: true
readiness_oracle:
  type: proof_contract
  claim: example
  required_proof: [example-proof]
decomposition:
  strategy: manual
  tasks: []
contracts:
  modules: []
  tasks: []
  proofs: []
  reviews: []
  integration: example-integration
---
# Missing objective
""",
        encoding="utf-8",
    )

    report = validate_path(tmp_path, schema_dir=SCHEMA_DIR, check_graph=False)

    assert not report.ok
    assert any("'objective' is a required property" in issue.message for issue in report.issues)


def test_graph_validation_reports_missing_referenced_contract(tmp_path: Path) -> None:
    source = ROOT / "examples" / "minimal"
    target = tmp_path / "minimal"
    shutil.copytree(source, target)
    goal_path = target / "GOAL_CONTRACT.md"
    goal_path.write_text(
        goal_path.read_text(encoding="utf-8").replace(
            "checkout-negative-total-proof", "missing-proof-contract"
        ),
        encoding="utf-8",
    )

    report = validate_path(target, schema_dir=SCHEMA_DIR)

    assert not report.ok
    assert any("missing proof contract: missing-proof-contract" in issue.message for issue in report.issues)
