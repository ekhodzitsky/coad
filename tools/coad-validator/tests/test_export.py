from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.artifact_export import export_artifacts

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
REPORT_SCHEMA_DIR = SCHEMA_DIR / "reports"


def test_export_artifacts_writes_bundle_manifest_and_reports(tmp_path: Path) -> None:
    output_dir = tmp_path / "coad-export"

    payload = export_artifacts(ROOT, schema_dir=SCHEMA_DIR, output_dir=output_dir)

    assert payload["ok"] is True
    assert payload["status"] == "exported"
    assert len(payload["bundle_digest"]) == 64
    assert payload["artifact_count"] == len(payload["artifacts"])
    assert {artifact["name"] for artifact in payload["artifacts"]} == {
        "attestation-report",
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
    assert (output_dir / "manifest.json").is_file()
    assert json.loads((output_dir / "manifest.json").read_text(encoding="utf-8")) == payload
    for artifact in payload["artifacts"]:
        artifact_path = output_dir / artifact["path"]
        assert artifact_path.is_file()
        assert len(artifact["digest"]) == 64
        assert artifact["bytes"] == artifact_path.stat().st_size
    _assert_matches_report_schema("export-report.schema.json", payload)


def test_export_artifacts_fails_when_required_report_fails(tmp_path: Path) -> None:
    target = _copy_repo_subset(tmp_path)
    (target / "examples" / "minimal" / "EXECUTION_LEDGER.json").unlink()

    payload = export_artifacts(target, schema_dir=target / "schema", output_dir=tmp_path / "coad-export")

    assert payload["ok"] is False
    assert payload["status"] == "export_failed"
    assert {
        "severity": "error",
        "path": "EXECUTION_LEDGER.json",
        "message": "required artifact report failed: ledger-report",
    } in payload["issues"]
    assert any(
        artifact["name"] == "ledger-report" and artifact["ok"] is False
        for artifact in payload["artifacts"]
    )
    _assert_matches_report_schema("export-report.schema.json", payload)


def test_export_cli_output_matches_schema(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.export_cli",
            str(ROOT),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--output-dir",
            str(tmp_path / "coad-export"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    _assert_matches_report_schema("export-report.schema.json", payload)


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
