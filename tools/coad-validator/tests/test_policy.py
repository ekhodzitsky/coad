from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.policy import build_policy_report

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
REPORT_SCHEMA_DIR = SCHEMA_DIR / "reports"
FIXTURES = Path(__file__).parent / "fixtures"


def test_policy_report_accepts_minimal_graph() -> None:
    payload = build_policy_report(FIXTURES / "valid" / "minimal-graph", schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["status"] == "pass"
    assert payload["issues"] == []
    assert payload["goals"][0]["goal_id"] == "checkout-negative-total-hardening"
    _assert_matches_report_schema("policy-report.schema.json", payload)


def test_policy_report_rejects_external_side_effects_when_goal_disallows_them(tmp_path: Path) -> None:
    target = _copy_minimal_graph(tmp_path)
    _replace_text(
        target / "TASK_CONTRACT.md",
        "handoff:\n",
        "external_side_effects:\n"
        "  - kind: network\n"
        "    target: https://api.example.invalid/deploy\n"
        "    reason: trigger deployment\n"
        "handoff:\n",
    )

    payload = build_policy_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert {
        "severity": "error",
        "path": "TASK_CONTRACT.md",
        "message": "task checkout-negative-total-guard declares external side effects but goal checkout-negative-total-hardening disallows them",
    } in payload["issues"]
    _assert_matches_report_schema("policy-report.schema.json", payload)


def test_policy_report_requires_contract_update_handoff_field(tmp_path: Path) -> None:
    target = _copy_minimal_graph(tmp_path)
    _replace_text(target / "TASK_CONTRACT.md", "    - contract_updates\n", "")

    payload = build_policy_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert {
        "severity": "error",
        "path": "TASK_CONTRACT.md",
        "message": "task checkout-negative-total-guard handoff must require contract_updates because goal checkout-negative-total-hardening requires contract updates",
    } in payload["issues"]


def test_policy_cli_output_matches_schema() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.policy_cli",
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
    _assert_matches_report_schema("policy-report.schema.json", payload)


def _copy_minimal_graph(tmp_path: Path) -> Path:
    target = tmp_path / "graph"
    shutil.copytree(FIXTURES / "valid" / "minimal-graph", target)
    return target


def _replace_text(path: Path, old: str, new: str) -> None:
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    schema_path = REPORT_SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
