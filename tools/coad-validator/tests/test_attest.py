from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.attest import build_attestation_report

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
REPORT_SCHEMA_DIR = SCHEMA_DIR / "reports"


def test_attestation_report_binds_required_reports() -> None:
    payload = build_attestation_report(ROOT, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["status"] == "attested"
    assert len(payload["bundle_digest"]) == 64
    assert {report["name"] for report in payload["reports"]} == {
        "agent-guidance",
        "validation-report",
        "status-report",
        "proof-matrix",
        "graph-report",
        "schedule-report",
        "ledger-report",
        "profile-report",
        "policy-report",
        "drift-report",
    }
    assert all(len(report["digest"]) == 64 for report in payload["reports"])
    assert all(report["required"] is True for report in payload["reports"])
    _assert_matches_report_schema("attestation-report.schema.json", payload)


def test_attestation_digest_is_stable_for_same_inputs() -> None:
    first = build_attestation_report(ROOT, schema_dir=SCHEMA_DIR)
    second = build_attestation_report(ROOT, schema_dir=SCHEMA_DIR)

    assert first["bundle_digest"] == second["bundle_digest"]


def test_attestation_report_fails_when_required_report_fails(tmp_path: Path) -> None:
    target = _copy_repo_subset(tmp_path)
    (target / "examples" / "minimal" / "EXECUTION_LEDGER.json").unlink()

    payload = build_attestation_report(target, schema_dir=target / "schema")

    assert payload["ok"] is False
    assert payload["status"] == "attestation_failed"
    assert {
        "severity": "error",
        "path": "EXECUTION_LEDGER.json",
        "message": "required attestation report failed: ledger-report",
    } in payload["issues"]
    assert any(report["name"] == "ledger-report" and report["ok"] is False for report in payload["reports"])
    _assert_matches_report_schema("attestation-report.schema.json", payload)


def test_attestation_cli_output_matches_schema() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.attest_cli",
            str(ROOT),
            "--schema-dir",
            str(SCHEMA_DIR),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    _assert_matches_report_schema("attestation-report.schema.json", payload)


def _copy_repo_subset(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(ROOT / ".github", target / ".github")
    shutil.copytree(ROOT / "docs", target / "docs")
    shutil.copytree(ROOT / "examples", target / "examples")
    shutil.copytree(ROOT / "schema", target / "schema")
    shutil.copytree(ROOT / "tools", target / "tools", ignore=shutil.ignore_patterns(".venv", "__pycache__"))
    shutil.copy2(ROOT / "COAD_PROFILE.json", target / "COAD_PROFILE.json")
    shutil.copy2(ROOT / "README.md", target / "README.md")
    return target


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    schema_path = REPORT_SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
