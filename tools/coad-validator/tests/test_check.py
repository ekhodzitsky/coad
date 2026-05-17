from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.check import build_check_report

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
REPORT_SCHEMA_DIR = SCHEMA_DIR / "reports"
FIXTURES = Path(__file__).parent / "fixtures"
MINIMAL_EXAMPLE = ROOT / "examples" / "minimal"
ONBOARDING_EXAMPLE = ROOT / "examples" / "onboarding"
BEFORE_AFTER_BEFORE = ROOT / "examples" / "before-after" / "before"
BEFORE_AFTER_AFTER = ROOT / "examples" / "before-after" / "after"
ONBOARDING_FIXTURE = FIXTURES / "valid" / "onboarding"
MISSING_CONSUMER_FIXTURE = FIXTURES / "invalid" / "missing-consumer"


def test_check_report_passes_for_valid_methodology_graph() -> None:
    payload = build_check_report(MINIMAL_EXAMPLE, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["status"] == "pass"
    assert {check["name"] for check in payload["checks"]} == {
        "agent-guidance",
        "validation-report",
        "status-report",
        "proof-matrix",
        "graph-report",
        "schedule-report",
        "ledger-report",
        "policy-report",
    }
    assert payload["issues"] == []
    _assert_matches_report_schema("check-report.schema.json", payload)


def test_check_report_passes_for_two_minute_onboarding_shape() -> None:
    payload = build_check_report(ONBOARDING_FIXTURE, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["status"] == "pass"
    check_names = {check["name"] for check in payload["checks"]}
    assert {"agent-guidance", "validation-report"}.issubset(check_names)
    assert "ledger-report" not in check_names
    assert payload["issues"] == []
    _assert_matches_report_schema("check-report.schema.json", payload)


def test_check_report_passes_for_public_onboarding_example() -> None:
    payload = build_check_report(ONBOARDING_EXAMPLE, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["status"] == "pass"
    assert {check["name"] for check in payload["checks"]} == {
        "agent-guidance",
        "validation-report",
    }
    assert payload["issues"] == []
    _assert_matches_report_schema("check-report.schema.json", payload)


def test_before_after_example_demonstrates_contract_quality_failure_and_fix() -> None:
    before = build_check_report(BEFORE_AFTER_BEFORE, schema_dir=SCHEMA_DIR)
    after = build_check_report(BEFORE_AFTER_AFTER, schema_dir=SCHEMA_DIR)

    assert before["ok"] is False
    assert before["status"] == "fail"
    assert {
        "code": "agent-guidance.failed",
        "severity": "error",
        "path": "AGENTS.md",
        "message": "agent-guidance: missing AGENTS.md with COAD onboarding guidance",
    } in before["issues"]

    assert after["ok"] is True
    assert after["status"] == "pass"
    assert after["issues"] == []
    _assert_matches_report_schema("check-report.schema.json", before)
    _assert_matches_report_schema("check-report.schema.json", after)


def test_check_report_catches_public_surface_without_consumer() -> None:
    payload = build_check_report(MISSING_CONSUMER_FIXTURE, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert payload["status"] == "fail"
    assert {
        "code": "semantic.public_surface_without_consumer",
        "severity": "error",
        "path": "MODULE_CONTRACT.md",
        "message": (
            "validation-report: public surface has no declared consumer: "
            "BillingTotals"
        ),
    } in payload["issues"]
    _assert_matches_report_schema("check-report.schema.json", payload)


def test_check_report_requires_root_agents_onboarding_guidance(tmp_path: Path) -> None:
    target = tmp_path / "onboarding"
    shutil.copytree(ONBOARDING_FIXTURE, target)
    (target / "AGENTS.md").unlink()

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert payload["status"] == "fail"
    assert {
        "code": "agent-guidance.failed",
        "severity": "error",
        "path": "AGENTS.md",
        "message": "agent-guidance: missing AGENTS.md with COAD onboarding guidance",
    } in payload["issues"]
    _assert_matches_report_schema("check-report.schema.json", payload)


def test_validator_package_exposes_only_coad_public_command() -> None:
    pyproject = ROOT / "tools" / "coad-validator" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    assert data["project"]["scripts"] == {
        "coad": "coad_validator.coad_cli:main",
    }


def test_check_report_fails_for_invalid_methodology_graph() -> None:
    payload = build_check_report(FIXTURES / "invalid" / "missing-proof", schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert payload["status"] == "fail"
    assert any(issue["path"] == "GOAL_CONTRACT.md" for issue in payload["issues"])
    assert any(check["name"] == "validation-report" and check["ok"] is False for check in payload["checks"])
    _assert_matches_report_schema("check-report.schema.json", payload)


def test_coad_check_text_output_is_one_line() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.coad_cli",
            "check",
            str(MINIMAL_EXAMPLE),
            "--schema-dir",
            str(SCHEMA_DIR),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout == "coad check: pass\n"
    assert result.stderr == ""


def test_coad_check_failure_text_output_is_one_line() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.coad_cli",
            "check",
            str(FIXTURES / "invalid" / "missing-proof"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert result.stdout == "coad check: fail\n"
    assert result.stderr == ""


def test_coad_check_uses_bundled_schemas_when_repo_has_no_schema_dir(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.coad_cli",
            "check",
            str(target),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout == "coad check: pass\n"
    assert result.stderr == ""


def test_coad_check_json_output_matches_schema() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.coad_cli",
            "check",
            str(MINIMAL_EXAMPLE),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    _assert_matches_report_schema("check-report.schema.json", payload)


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    schema_path = REPORT_SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
