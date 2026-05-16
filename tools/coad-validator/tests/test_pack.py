from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_pack_outputs_bounded_context_for_task() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.pack_cli",
            "checkout-negative-total-guard",
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

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["task_id"] == "checkout-negative-total-guard"
    assert payload["goal"]["id"] == "checkout-negative-total-hardening"
    assert payload["task"]["id"] == "checkout-negative-total-guard"
    assert [module["id"] for module in payload["modules"]] == ["checkout"]
    assert [proof["id"] for proof in payload["proofs"]] == ["checkout-negative-total-proof"]
    assert [review["id"] for review in payload["reviews"]] == ["checkout-negative-total-review"]
    assert [handoff["id"] for handoff in payload["handoffs"]] == ["checkout-negative-total-guard"]
    assert payload["integration"]["id"] == "checkout-negative-total-integration"
    assert payload["contracts"] == [
        "GOAL_CONTRACT.md",
        "TASK_CONTRACT.md",
        "MODULE_CONTRACT.md",
        "PROOF.md",
        "REVIEW.md",
        "HANDOFF.md",
        "INTEGRATION.md",
    ]


def test_cli_pack_reports_missing_task() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.pack_cli",
            "missing-task",
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

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload == {
        "schema_version": 1,
        "ok": False,
        "error": "task contract not found: missing-task",
    }
