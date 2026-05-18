from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.ledger import build_ledger_report

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
REPORT_SCHEMA_DIR = SCHEMA_DIR / "reports"
FIXTURES = Path(__file__).parent / "fixtures"


def test_ledger_report_accepts_completed_task_with_required_proof(tmp_path: Path) -> None:
    target = _copy_minimal_graph(tmp_path)
    _write_ledger(
        target / "EXECUTION_LEDGER.json",
        proof_results=[
            {
                "command": "test checkout.checkout_service.rejects_negative_total",
                "status": "pass",
                "artifact": "artifacts/unit-test.txt",
            },
            {
                "command": "test schemas/checkout-decision.schema.json",
                "status": "pass",
                "artifact": "artifacts/schema-test.txt",
            },
        ],
    )

    payload = build_ledger_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["status"] == "verified"
    entry = payload["ledgers"][0]["entries"][0]
    assert entry["task_id"] == "checkout-negative-total-guard"
    assert entry["proof_status"] == "complete"
    assert entry["required_proof_commands"] == [
        "test checkout.checkout_service.rejects_negative_total",
        "test schemas/checkout-decision.schema.json",
    ]
    _assert_matches_report_schema("ledger-report.schema.json", payload)


def test_ledger_report_rejects_completed_task_missing_required_proof(tmp_path: Path) -> None:
    target = _copy_minimal_graph(tmp_path)
    _write_ledger(
        target / "EXECUTION_LEDGER.json",
        proof_results=[
            {
                "command": "test checkout.checkout_service.rejects_negative_total",
                "status": "pass",
                "artifact": "artifacts/unit-test.txt",
            },
        ],
    )

    payload = build_ledger_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert payload["status"] == "ledger_issues"
    assert {
        "severity": "error",
        "path": "EXECUTION_LEDGER.json",
        "message": "completed task checkout-negative-total-guard missing passing proof command: test schemas/checkout-decision.schema.json",
    } in payload["issues"]
    _assert_matches_report_schema("ledger-report.schema.json", payload)


def test_ledger_report_rejects_non_object_ledger_json(tmp_path: Path) -> None:
    target = _copy_minimal_graph(tmp_path)
    (target / "EXECUTION_LEDGER.json").write_text("[]", encoding="utf-8")

    payload = build_ledger_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert {
        "severity": "error",
        "path": "EXECUTION_LEDGER.json",
        "message": "execution ledger must be a JSON object",
    } in payload["issues"]
    _assert_matches_report_schema("ledger-report.schema.json", payload)


def test_ledger_cli_output_matches_schema(tmp_path: Path) -> None:
    target = _copy_minimal_graph(tmp_path)
    _write_ledger(
        target / "EXECUTION_LEDGER.json",
        proof_results=[
            {
                "command": "test checkout.checkout_service.rejects_negative_total",
                "status": "pass",
                "artifact": "artifacts/unit-test.txt",
            },
            {
                "command": "test schemas/checkout-decision.schema.json",
                "status": "pass",
                "artifact": "artifacts/schema-test.txt",
            },
        ],
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.ledger_cli",
            str(target),
            "--schema-dir",
            str(SCHEMA_DIR),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    _assert_matches_report_schema("ledger-report.schema.json", payload)


def _copy_minimal_graph(tmp_path: Path) -> Path:
    target = tmp_path / "graph"
    shutil.copytree(FIXTURES / "valid" / "minimal-graph", target)
    return target


def _write_ledger(path: Path, proof_results: list[dict[str, Any]]) -> None:
    for proof_result in proof_results:
        if proof_result.get("status") != "pass" or "artifact" not in proof_result:
            continue
        artifact = path.parent / str(proof_result["artifact"])
        payload = artifact.read_bytes()
        proof_result["artifact_sha256"] = hashlib.sha256(payload).hexdigest()
        proof_result["artifact_bytes"] = len(payload)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "kind": "execution_ledger",
                "run_id": "run-checkout-negative-total",
                "goal_id": "checkout-negative-total-hardening",
                "entries": [
                    {
                        "event_id": "event-checkout-negative-total-completed",
                        "task_id": "checkout-negative-total-guard",
                        "wave": 1,
                        "agent_id": "codex-main",
                        "role": "executor",
                        "status": "completed",
                        "started_at": "2026-05-16T11:00:00Z",
                        "completed_at": "2026-05-16T11:05:00Z",
                        "proof_results": proof_results,
                        "changed_files": ["checkout/service.py"],
                        "handoff_path": "HANDOFF.md",
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    schema_path = REPORT_SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
