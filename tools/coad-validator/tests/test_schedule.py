from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.schedule import build_schedule_report

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
REPORT_SCHEMA_DIR = SCHEMA_DIR / "reports"
FIXTURES = Path(__file__).parent / "fixtures"


def test_schedule_report_groups_tasks_into_dependency_waves(tmp_path: Path) -> None:
    target = _copy_minimal_graph(tmp_path)
    _replace_text(target / "GOAL_CONTRACT.md", "max_parallel_agents: 1", "max_parallel_agents: 2")
    _add_goal_task(target / "GOAL_CONTRACT.md", "checkout-doc-update")
    _add_goal_task(target / "GOAL_CONTRACT.md", "checkout-followup")
    _add_integration_task(target / "INTEGRATION.md", "checkout-doc-update")
    _add_integration_task(target / "INTEGRATION.md", "checkout-followup")
    _write_task(
        target / "TASK_DOC.md",
        task_id="checkout-doc-update",
        write_scope=["docs/checkout.md"],
        dependencies=[],
    )
    _write_task(
        target / "TASK_FOLLOWUP.md",
        task_id="checkout-followup",
        write_scope=["docs/checkout-followup.md"],
        dependencies=["checkout-negative-total-guard"],
    )

    payload = build_schedule_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    goal = payload["goals"][0]
    assert goal["max_parallel_agents"] == 2
    assert [
        [task["task_id"] for task in wave["tasks"]]
        for wave in goal["waves"]
    ] == [
        ["checkout-negative-total-guard", "checkout-doc-update"],
        ["checkout-followup"],
    ]
    assert goal["blocked"] == []
    _assert_matches_report_schema("schedule-report.schema.json", payload)


def test_schedule_report_serializes_write_scope_conflicts(tmp_path: Path) -> None:
    target = _copy_minimal_graph(tmp_path)
    _replace_text(target / "GOAL_CONTRACT.md", "max_parallel_agents: 1", "max_parallel_agents: 2")
    _add_goal_task(target / "GOAL_CONTRACT.md", "checkout-overlap")
    _add_integration_task(target / "INTEGRATION.md", "checkout-overlap")
    _write_task(
        target / "TASK_OVERLAP.md",
        task_id="checkout-overlap",
        write_scope=["checkout/service.py"],
        dependencies=[],
    )

    payload = build_schedule_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    goal = payload["goals"][0]
    assert [
        [task["task_id"] for task in wave["tasks"]]
        for wave in goal["waves"]
    ] == [
        ["checkout-negative-total-guard"],
        ["checkout-overlap"],
    ]
    assert {
        "task_a": "checkout-negative-total-guard",
        "task_b": "checkout-overlap",
        "type": "write_scope_overlap",
        "scopes": ["checkout/**", "checkout/service.py"],
    } in goal["conflicts"]


def test_schedule_cli_output_matches_schema() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.schedule_cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    _assert_matches_report_schema("schedule-report.schema.json", payload)


def _copy_minimal_graph(tmp_path: Path) -> Path:
    target = tmp_path / "graph"
    shutil.copytree(FIXTURES / "valid" / "minimal-graph", target)
    return target


def _write_task(
    path: Path,
    *,
    task_id: str,
    write_scope: list[str],
    dependencies: list[str],
) -> None:
    write_scope_yaml = "\n".join(f"  - {scope}" for scope in write_scope)
    dependencies_yaml = (
        "dependencies:\n" + "\n".join(f"  - {dependency}" for dependency in dependencies)
        if dependencies
        else "dependencies: []"
    )
    path.write_text(
        f"""---
schema_version: 1
kind: task_contract
task_id: {task_id}
objective: Exercise schedule planning.
owner_role: executor
status: pending
risk: medium
change_class: documentation
modules:
  - checkout
read_scope:
  - checkout/**
write_scope:
{write_scope_yaml}
{dependencies_yaml}
allowed_mutations:
  - update scoped files
forbidden_mutations:
  - change public checkout schema
acceptance:
  - Schedule report includes this task.
proof:
  required:
    - proof_id: checkout-negative-total-proof
      kind: unit-test
      target: checkout.schedule
      command: test checkout.schedule
handoff:
  required_fields:
    - changed_files
    - proof_results
    - contract_updates
    - known_gaps
---

# {task_id}
""",
        encoding="utf-8",
    )


def _add_goal_task(path: Path, task_id: str) -> None:
    _replace_text(path, "    - checkout-negative-total-guard\n", f"    - checkout-negative-total-guard\n    - {task_id}\n")


def _add_integration_task(path: Path, task_id: str) -> None:
    _replace_text(path, "  - checkout-negative-total-guard\n", f"  - checkout-negative-total-guard\n  - {task_id}\n")


def _replace_text(path: Path, old: str, new: str) -> None:
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    schema_path = REPORT_SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
