from __future__ import annotations

import json
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

from coad_validator.validate import validate_path

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
FIXTURES = Path(__file__).parent / "fixtures"
PROJECT_SELF_MODULES = {
    "contracts",
    "docs",
    "examples",
    "playbooks",
    "schema",
    "templates",
    "tools/coad-validator",
}


def test_minimal_example_validates() -> None:
    report = validate_path(ROOT / "examples" / "minimal", schema_dir=SCHEMA_DIR)

    assert report.ok, [issue.format(report.root) for issue in report.issues]
    assert len(report.documents) == 7


def test_valid_conformance_fixture_validates() -> None:
    report = validate_path(FIXTURES / "valid" / "minimal-graph", schema_dir=SCHEMA_DIR)

    assert report.ok, [issue.format(report.root) for issue in report.issues]
    assert len(report.documents) == 7


def test_repository_validation_skips_templates_and_test_fixtures() -> None:
    report = validate_path(ROOT, schema_dir=SCHEMA_DIR)

    assert report.ok, [issue.format(report.root) for issue in report.issues]
    assert len(report.documents) == 37


def test_repository_declares_real_project_module_contracts() -> None:
    report = validate_path(ROOT, schema_dir=SCHEMA_DIR)

    modules = {
        document.data["module"]
        for document in report.documents
        if document.kind == "module_contract"
    }
    assert PROJECT_SELF_MODULES.issubset(modules)


def test_repository_self_contracts_do_not_need_budget_exceptions() -> None:
    report = validate_path(ROOT, schema_dir=SCHEMA_DIR)

    exceptions = [
        document.identifier
        for document in report.documents
        if document.path.parent == ROOT / "project-contracts"
        and isinstance(document.data.get("workcell"), dict)
        and document.data["workcell"].get("budget_exceptions")
    ]

    assert exceptions == []


def test_methodology_entry_docs_are_discoverable() -> None:
    expected_docs = [
        ROOT / "COAD_PROJECT_STANDARD.md",
        ROOT / "AGENT_FLOW.md",
    ]
    for path in expected_docs:
        assert path.is_file()

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    for path in expected_docs:
        assert path.name in readme
        assert path.name in docs_readme


def test_invalid_conformance_fixture_reports_missing_proof() -> None:
    report = validate_path(FIXTURES / "invalid" / "missing-proof", schema_dir=SCHEMA_DIR)

    assert not report.ok
    assert any("missing proof contract: missing-proof-contract" in issue.message for issue in report.issues)


def test_cli_json_output_for_valid_fixture() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload == {
        "schema_version": 1,
        "ok": True,
        "contracts": 7,
        "issues": [],
    }


def test_cli_json_output_for_invalid_fixture_reports_structured_issue() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.cli",
            str(FIXTURES / "invalid" / "missing-proof"),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["contracts"] == 6
    assert payload["issues"][0]["severity"] == "error"
    assert payload["issues"][0]["path"] == "GOAL_CONTRACT.md"
    assert "missing proof contract: missing-proof-contract" in payload["issues"][0]["message"]


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


def test_module_contract_requires_agent_context_files(tmp_path: Path) -> None:
    source = ROOT / "examples" / "minimal"
    target = tmp_path / "minimal"
    shutil.copytree(source, target)
    shutil.rmtree(target / "checkout")

    report = validate_path(target, schema_dir=SCHEMA_DIR)

    assert not report.ok
    assert any("module directory does not exist: checkout" in issue.message for issue in report.issues)


def test_module_contract_requires_readme_and_todo(tmp_path: Path) -> None:
    source = ROOT / "examples" / "minimal"
    target = tmp_path / "minimal"
    shutil.copytree(source, target)
    (target / "checkout" / "README.md").unlink()
    (target / "checkout" / "TODO.md").unlink()

    report = validate_path(target, schema_dir=SCHEMA_DIR)

    assert not report.ok
    assert any("module agent context is missing README.md" in issue.message for issue in report.issues)
    assert any("module agent context is missing TODO.md" in issue.message for issue in report.issues)


def test_module_contract_enforces_workcell_context_budgets(tmp_path: Path) -> None:
    source = ROOT / "examples" / "minimal"
    target = tmp_path / "minimal"
    shutil.copytree(source, target)
    contract_path = target / "MODULE_CONTRACT.md"
    contract_path.write_text(
        contract_path.read_text(encoding="utf-8")
        .replace("max_files: 12", "max_files: 2")
        .replace("max_source_lines: 1500", "max_source_lines: 1")
        .replace("max_contract_lines: 180", "max_contract_lines: 10")
        .replace("max_readme_lines: 120", "max_readme_lines: 2")
        .replace("max_todo_lines: 80", "max_todo_lines: 2")
        .replace("max_surfaces: 8", "max_surfaces: 1")
        .replace("max_invariants: 8", "max_invariants: 0"),
        encoding="utf-8",
    )
    (target / "checkout" / "extra.py").write_text("print('extra')\n", encoding="utf-8")
    (target / "checkout" / "logic.py").write_text("a = 1\nb = 2\n", encoding="utf-8")
    (target / "checkout" / "README.md").write_text("one\ntwo\nthree\n", encoding="utf-8")
    (target / "checkout" / "TODO.md").write_text("one\ntwo\nthree\n", encoding="utf-8")

    report = validate_path(target, schema_dir=SCHEMA_DIR)

    messages = [issue.message for issue in report.issues]
    assert not report.ok
    assert any("workcell budget exceeded: max_files" in message for message in messages)
    assert any("workcell budget exceeded: max_source_lines" in message for message in messages)
    assert any("workcell budget exceeded: max_contract_lines" in message for message in messages)
    assert any("workcell budget exceeded: max_readme_lines" in message for message in messages)
    assert any("workcell budget exceeded: max_todo_lines" in message for message in messages)
    assert any("workcell budget exceeded: max_surfaces" in message for message in messages)
    assert any("workcell budget exceeded: max_invariants" in message for message in messages)


def test_module_contract_allows_documented_workcell_budget_exception(tmp_path: Path) -> None:
    source = ROOT / "examples" / "minimal"
    target = tmp_path / "minimal"
    shutil.copytree(source, target)
    contract_path = target / "MODULE_CONTRACT.md"
    contract_path.write_text(
        contract_path.read_text(encoding="utf-8")
        .replace("max_files: 12", "max_files: 2")
        .replace("max_source_lines: 1500", "max_source_lines: 1")
        .replace("max_contract_lines: 180", "max_contract_lines: 10")
        .replace("max_readme_lines: 120", "max_readme_lines: 2")
        .replace("max_todo_lines: 80", "max_todo_lines: 2")
        .replace("max_surfaces: 8", "max_surfaces: 1")
        .replace("max_invariants: 8", "max_invariants: 0")
        .replace(
            "    max_invariants: 0\nauthority:",
            "    max_invariants: 0\n"
            "  budget_exceptions:\n"
            "    - metric: context_budget\n"
            "      reason: Legacy fixture intentionally exceeds all budgets while awaiting split.\n"
            "authority:",
        ),
        encoding="utf-8",
    )
    (target / "checkout" / "extra.py").write_text("print('extra')\n", encoding="utf-8")
    (target / "checkout" / "logic.py").write_text("a = 1\nb = 2\n", encoding="utf-8")
    (target / "checkout" / "README.md").write_text("one\ntwo\nthree\n", encoding="utf-8")
    (target / "checkout" / "TODO.md").write_text("one\ntwo\nthree\n", encoding="utf-8")

    report = validate_path(target, schema_dir=SCHEMA_DIR)

    assert report.ok, [issue.format(report.root) for issue in report.issues]


def test_module_contract_can_use_logical_module_with_context_path(tmp_path: Path) -> None:
    module_dir = tmp_path / "src" / "checkout"
    module_dir.mkdir(parents=True)
    (module_dir / "README.md").write_text("# checkout\n", encoding="utf-8")
    (module_dir / "TODO.md").write_text("# checkout TODO\n", encoding="utf-8")
    contract_path = tmp_path / "MODULE_CONTRACT.md"
    contract_path.write_text(
        """---
schema_version: 1
kind: module_contract
module: commerce/checkout
level: subsystem
purpose: Logical checkout workcell backed by an existing source directory.
status: pilot
workcell:
  type: leaf
  context_path: src/checkout
  owns_paths:
    - src/checkout/README.md
    - src/checkout/TODO.md
  context_budget:
    max_files: 2
    max_source_lines: 1
    max_contract_lines: 80
    max_readme_lines: 10
    max_todo_lines: 10
    max_surfaces: 1
    max_invariants: 0
surface:
  - name: Checkout
    kind: module
    visibility: internal
    contract: Owns checkout decisions.
    proof:
      kind: static-check
      target: src/checkout
      command: test checkout
dependencies:
  internal: []
  external: []
consumers: []
invariants: []
verification:
  pre_change:
    - test checkout
  full:
    - test all
---
# commerce/checkout
""",
        encoding="utf-8",
    )

    report = validate_path(tmp_path, schema_dir=SCHEMA_DIR, check_graph=False)

    assert report.ok, [issue.format(report.root) for issue in report.issues]


def test_release_metadata_requires_version_and_changelog_for_validator_repo(tmp_path: Path) -> None:
    validator_dir = tmp_path / "tools" / "coad-validator"
    validator_dir.mkdir(parents=True)
    (validator_dir / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            name = "coad-validator"
            version = "0.1.0"
            """
        ).strip(),
        encoding="utf-8",
    )

    report = validate_path(tmp_path, schema_dir=SCHEMA_DIR, check_graph=False)

    assert not report.ok
    assert any("release metadata is missing VERSION" in issue.message for issue in report.issues)
    assert any("release metadata is missing CHANGELOG.md" in issue.message for issue in report.issues)


def test_release_metadata_requires_pyproject_version_to_match_version_file(tmp_path: Path) -> None:
    validator_dir = tmp_path / "tools" / "coad-validator"
    validator_dir.mkdir(parents=True)
    (validator_dir / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            name = "coad-validator"
            version = "0.1.0"
            """
        ).strip(),
        encoding="utf-8",
    )
    (tmp_path / "VERSION").write_text("0.2.0\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## 0.2.0 - 2026-05-16\n", encoding="utf-8")

    report = validate_path(tmp_path, schema_dir=SCHEMA_DIR, check_graph=False)

    assert not report.ok
    assert any("pyproject version 0.1.0 does not match VERSION 0.2.0" in issue.message for issue in report.issues)


def test_release_metadata_requires_changelog_entry_for_current_version(tmp_path: Path) -> None:
    validator_dir = tmp_path / "tools" / "coad-validator"
    validator_dir.mkdir(parents=True)
    (validator_dir / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            name = "coad-validator"
            version = "0.1.0"
            """
        ).strip(),
        encoding="utf-8",
    )
    (tmp_path / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## 0.0.9 - 2026-05-15\n", encoding="utf-8")

    report = validate_path(tmp_path, schema_dir=SCHEMA_DIR, check_graph=False)

    assert not report.ok
    assert any("CHANGELOG.md is missing an entry for VERSION 0.1.0" in issue.message for issue in report.issues)


def test_release_metadata_requires_package_version_to_match_version_file(tmp_path: Path) -> None:
    validator_dir = tmp_path / "tools" / "coad-validator"
    package_dir = validator_dir / "src" / "coad_validator"
    package_dir.mkdir(parents=True)
    (validator_dir / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            name = "coad-validator"
            version = "0.1.0"
            """
        ).strip(),
        encoding="utf-8",
    )
    (package_dir / "__init__.py").write_text('__version__ = "0.0.9"\n', encoding="utf-8")
    (tmp_path / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## 0.1.0 - 2026-05-16\n", encoding="utf-8")

    report = validate_path(tmp_path, schema_dir=SCHEMA_DIR, check_graph=False)

    assert not report.ok
    assert any("package __version__ 0.0.9 does not match VERSION 0.1.0" in issue.message for issue in report.issues)
