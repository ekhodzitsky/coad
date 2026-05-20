from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.proof_matrix import build_proof_matrix

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
REPORT_SCHEMA_DIR = SCHEMA_DIR / "reports"
FIXTURES = Path(__file__).parent / "fixtures"


def test_proof_matrix_marks_satisfied_task_proofs_ready() -> None:
    payload = build_proof_matrix(FIXTURES / "valid" / "minimal-graph", schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["ready"] is True
    goal = payload["goals"][0]
    assert goal["status"] == "ready"
    task = goal["tasks"][0]
    assert task["status"] == "ready"
    assert [proof["status"] for proof in task["proofs"]] == ["pass", "pass"]
    assert [proof["proof_id"] for proof in task["proofs"]] == [
        "checkout-negative-total-proof",
        "checkout-negative-total-proof",
    ]


def test_proof_matrix_reports_missing_handoff_evidence(tmp_path: Path) -> None:
    source = FIXTURES / "valid" / "minimal-graph"
    target = tmp_path / "missing-evidence"
    shutil.copytree(source, target)
    handoff_path = target / "HANDOFF.md"
    handoff_path.write_text(
        handoff_path.read_text(encoding="utf-8").replace(
            "test schemas/checkout-decision.schema.json",
            "test schemas/missing-schema.schema.json",
        ),
        encoding="utf-8",
    )

    payload = build_proof_matrix(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["ready"] is False
    proof = payload["goals"][0]["tasks"][0]["proofs"][1]
    assert proof["status"] == "missing_evidence"
    assert proof["evidence"] is None
    assert "missing passing evidence" in payload["goals"][0]["blockers"][0]["message"]


def test_proof_matrix_cli_reports_invalid_contracts() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.proof_matrix_cli",
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
    assert payload["ready"] is False
    assert payload["status"] == "invalid"
    assert "missing proof contract: missing-proof-contract" in payload["issues"][0]["message"]
    _assert_matches_report_schema("proof-matrix.schema.json", payload)


def test_proof_matrix_cli_output_matches_report_schema() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.proof_matrix_cli",
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
    _assert_matches_report_schema("proof-matrix.schema.json", payload)


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    schema_path = REPORT_SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
