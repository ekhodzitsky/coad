from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.profile import build_profile_report

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
REPORT_SCHEMA_DIR = SCHEMA_DIR / "reports"


def test_profile_report_verifies_current_repository() -> None:
    payload = build_profile_report(ROOT, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["status"] == "conformant"
    assert payload["profile_id"] == "coad-ledger-audited-orchestration"
    assert payload["level"] == "ledger_audited_orchestration"
    assert {check["id"]: check["status"] for check in payload["checks"]} == {
        "contracts-valid": "pass",
        "schedule-builds": "pass",
        "execution-ledger-verified": "pass",
        "policy-enforced": "pass",
        "release-gates-clean": "pass",
    }
    _assert_matches_report_schema("profile-report.schema.json", payload)


def test_profile_report_fails_when_required_ledger_check_fails(tmp_path: Path) -> None:
    target = _copy_repo_subset(tmp_path)
    (target / "examples" / "minimal" / "EXECUTION_LEDGER.json").unlink()

    payload = build_profile_report(target, schema_dir=target / "schema")

    assert payload["ok"] is False
    assert payload["status"] == "nonconformant"
    assert {
        "severity": "error",
        "path": "COAD_PROFILE.json",
        "message": "required profile check failed: execution-ledger-verified",
    } in payload["issues"]
    assert {
        "id": "execution-ledger-verified",
        "status": "fail",
        "required": True,
        "evidence": "coad-ledger status=ledger_issues",
    } in payload["checks"]
    _assert_matches_report_schema("profile-report.schema.json", payload)


def test_profile_cli_output_matches_schema() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.profile_cli",
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
    _assert_matches_report_schema("profile-report.schema.json", payload)


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
