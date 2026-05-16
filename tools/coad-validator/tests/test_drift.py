from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.drift import build_drift_report

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
REPORT_SCHEMA_DIR = SCHEMA_DIR / "reports"


def test_drift_report_accepts_current_repository() -> None:
    payload = build_drift_report(ROOT)

    assert payload == {
        "schema_version": 1,
        "ok": True,
        "status": "clean",
        "issues": [],
    }
    _assert_matches_report_schema("drift-report.schema.json", payload)


def test_drift_report_detects_missing_tool_docs(tmp_path: Path) -> None:
    target = _copy_repo_subset(tmp_path)
    tools_readme = target / "tools" / "README.md"
    tools_readme.write_text(
        tools_readme.read_text(encoding="utf-8").replace(
            "- `coad-graph` - exports contract nodes and typed graph edges.\n",
            "",
        ),
        encoding="utf-8",
    )

    payload = build_drift_report(target)

    assert payload["ok"] is False
    assert payload["status"] == "drift"
    assert {
        "severity": "error",
        "path": "tools/README.md",
        "message": "missing documented tool: coad-graph",
    } in payload["issues"]
    _assert_matches_report_schema("drift-report.schema.json", payload)


def test_drift_report_detects_unlisted_report_schema(tmp_path: Path) -> None:
    target = _copy_repo_subset(tmp_path)
    manifest = target / "schema" / "report-manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["reports"] = [
        report
        for report in payload["reports"]
        if report["schema"] != "reports/graph-report.schema.json"
    ]
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    payload = build_drift_report(target)

    assert payload["ok"] is False
    assert {
        "severity": "error",
        "path": "schema/report-manifest.json",
        "message": "report schema missing from manifest: reports/graph-report.schema.json",
    } in payload["issues"]


def test_drift_report_detects_missing_release_gate_ci_step(tmp_path: Path) -> None:
    target = _copy_repo_subset(tmp_path)
    workflow = target / ".github" / "workflows" / "ci.yml"
    workflow.write_text(
        workflow.read_text(encoding="utf-8").replace(
            "      - name: Export contract graph\n"
            "        working-directory: tools/coad-validator\n"
            "        run: uv run --locked coad-graph ../.. --schema-dir ../../schema\n\n",
            "",
        ),
        encoding="utf-8",
    )

    payload = build_drift_report(target)

    assert payload["ok"] is False
    assert {
        "severity": "error",
        "path": ".github/workflows/ci.yml",
        "message": "release gate missing from CI: contract-graph-export",
    } in payload["issues"]


def test_drift_report_detects_release_gate_working_directory_drift(tmp_path: Path) -> None:
    target = _copy_repo_subset(tmp_path)
    workflow = target / ".github" / "workflows" / "ci.yml"
    workflow.write_text(
        workflow.read_text(encoding="utf-8").replace(
            "      - name: Export contract graph\n"
            "        working-directory: tools/coad-validator\n"
            "        run: uv run --locked coad-graph ../.. --schema-dir ../../schema\n",
            "      - name: Export contract graph\n"
            "        working-directory: .\n"
            "        run: uv run --locked coad-graph ../.. --schema-dir ../../schema\n",
        ),
        encoding="utf-8",
    )

    payload = build_drift_report(target)

    assert payload["ok"] is False
    assert {
        "severity": "error",
        "path": ".github/workflows/ci.yml",
        "message": "release gate missing from CI: contract-graph-export",
    } in payload["issues"]


def test_drift_cli_reports_structured_issues(tmp_path: Path) -> None:
    target = _copy_repo_subset(tmp_path)
    workflow = target / ".github" / "workflows" / "ci.yml"
    workflow.write_text(
        workflow.read_text(encoding="utf-8").replace(
            "      - name: Export contract graph\n"
            "        working-directory: tools/coad-validator\n"
            "        run: uv run --locked coad-graph ../.. --schema-dir ../../schema\n\n",
            "",
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "coad_validator.drift_cli", str(target)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert {
        "severity": "error",
        "path": ".github/workflows/ci.yml",
        "message": "CI does not run tool: coad-graph",
    } in payload["issues"]


def _copy_repo_subset(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(ROOT / ".github", target / ".github")
    shutil.copytree(ROOT / "docs", target / "docs")
    shutil.copytree(ROOT / "schema", target / "schema")
    shutil.copytree(ROOT / "tools", target / "tools", ignore=shutil.ignore_patterns(".venv"))
    return target


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    schema_path = REPORT_SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
