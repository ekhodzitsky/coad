from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.graph_report import build_graph_report

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
REPORT_SCHEMA_DIR = SCHEMA_DIR / "reports"
FIXTURES = Path(__file__).parent / "fixtures"


def test_graph_report_lists_contract_nodes_and_edges() -> None:
    payload = build_graph_report(FIXTURES / "valid" / "minimal-graph", schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["contracts"] == 7
    assert len(payload["nodes"]) == 7
    assert {
        "key": "task_contract:checkout-negative-total-guard",
        "id": "checkout-negative-total-guard",
        "kind": "task_contract",
        "path": "TASK_CONTRACT.md",
    } in payload["nodes"]
    assert len({node["key"] for node in payload["nodes"]}) == len(payload["nodes"])
    assert {
        "source": "goal_contract:checkout-negative-total-hardening",
        "target": "task_contract:checkout-negative-total-guard",
        "relation": "goal_has_task",
    } in payload["edges"]
    assert {
        "source": "task_contract:checkout-negative-total-guard",
        "target": "module_contract:checkout",
        "relation": "task_touches_module",
    } in payload["edges"]
    assert {
        "source": "task_contract:checkout-negative-total-guard",
        "target": "proof_contract:checkout-negative-total-proof",
        "relation": "task_requires_proof",
    } in payload["edges"]


def test_graph_report_cli_output_matches_schema() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.graph_report_cli",
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
    _assert_matches_report_schema("graph-report.schema.json", payload)


def test_graph_report_cli_reports_invalid_contracts() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.graph_report_cli",
            str(FIXTURES / "invalid" / "missing-proof"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["status"] == "invalid"
    assert "missing proof contract: missing-proof-contract" in payload["issues"][0]["message"]
    _assert_matches_report_schema("graph-report.schema.json", payload)


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    schema_path = REPORT_SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
