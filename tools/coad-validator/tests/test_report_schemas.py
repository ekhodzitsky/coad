from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.report_sources import ATTESTATION_SOURCES

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
REPORT_SCHEMA_DIR = SCHEMA_DIR / "reports"
FIXTURES = Path(__file__).parent / "fixtures"


def test_validate_json_output_matches_report_schema() -> None:
    valid = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--format",
            "json",
        ]
    )
    invalid = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.cli",
            str(FIXTURES / "invalid" / "missing-proof"),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--format",
            "json",
        ]
    )

    _assert_matches_report_schema("validation-report.schema.json", valid)
    _assert_matches_report_schema("validation-report.schema.json", invalid)


def test_check_json_output_matches_report_schema() -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.coad_cli",
            "check",
            str(ROOT / "examples" / "minimal"),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--format",
            "json",
        ]
    )

    _assert_matches_report_schema("check-report.schema.json", payload)


def test_status_json_output_matches_report_schema() -> None:
    valid = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.status_cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ]
    )
    invalid = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.status_cli",
            str(FIXTURES / "invalid" / "missing-proof"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ]
    )

    _assert_matches_report_schema("status-report.schema.json", valid)
    _assert_matches_report_schema("status-report.schema.json", invalid)


def test_context_pack_json_output_matches_report_schema() -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.pack_cli",
            "checkout-negative-total-guard",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ]
    )

    _assert_matches_report_schema("context-pack.schema.json", payload)


def test_schedule_json_output_matches_report_schema() -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.schedule_cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ]
    )

    _assert_matches_report_schema("schedule-report.schema.json", payload)


def test_ledger_json_output_matches_report_schema() -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.ledger_cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ]
    )

    _assert_matches_report_schema("ledger-report.schema.json", payload)


def test_profile_json_output_matches_report_schema() -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.profile_cli",
            str(ROOT),
            "--schema-dir",
            str(SCHEMA_DIR),
        ]
    )

    _assert_matches_report_schema("profile-report.schema.json", payload)


def test_policy_json_output_matches_report_schema() -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.policy_cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ]
    )

    _assert_matches_report_schema("policy-report.schema.json", payload)


def test_attestation_json_output_matches_report_schema() -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.attest_cli",
            str(ROOT),
            "--schema-dir",
            str(SCHEMA_DIR),
        ]
    )

    _assert_matches_report_schema("attestation-report.schema.json", payload)


def test_export_json_output_matches_report_schema(tmp_path: Path) -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.export_cli",
            str(ROOT),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--output-dir",
            str(tmp_path / "coad-export"),
        ]
    )

    _assert_matches_report_schema("export-report.schema.json", payload)


def test_pack_error_json_output_matches_report_schema() -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.pack_cli",
            "missing-task",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ]
    )

    _assert_matches_report_schema("pack-error.schema.json", payload)


def test_report_manifest_matches_manifest_schema() -> None:
    manifest_path = SCHEMA_DIR / "report-manifest.json"
    manifest_schema_path = SCHEMA_DIR / "report-manifest.schema.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_schema = json.loads(manifest_schema_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(manifest_schema)
    Draft202012Validator(manifest_schema).validate(manifest)
    for report in manifest["reports"]:
        assert (SCHEMA_DIR / report["schema"]).is_file()
    assert {source.name for source in ATTESTATION_SOURCES} <= {report["name"] for report in manifest["reports"]}


def test_release_manifest_matches_manifest_schema() -> None:
    manifest_path = SCHEMA_DIR / "release-manifest.json"
    manifest_schema_path = SCHEMA_DIR / "release-manifest.schema.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_schema = json.loads(manifest_schema_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(manifest_schema)
    Draft202012Validator(manifest_schema).validate(manifest)
    assert all(gate["required"] is True for gate in manifest["release_gates"])


def test_example_execution_ledger_matches_ledger_schema() -> None:
    ledger_path = ROOT / "examples" / "minimal" / "EXECUTION_LEDGER.json"
    ledger_schema_path = SCHEMA_DIR / "execution-ledger.schema.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger_schema = json.loads(ledger_schema_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(ledger_schema)
    Draft202012Validator(ledger_schema).validate(ledger)


def test_conformance_profile_matches_profile_schema() -> None:
    profile_path = ROOT / "COAD_PROFILE.json"
    profile_schema_path = SCHEMA_DIR / "conformance-profile.schema.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    profile_schema = json.loads(profile_schema_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(profile_schema)
    Draft202012Validator(profile_schema).validate(profile)


def test_bundled_schemas_match_repository_schemas() -> None:
    bundled_schema_dir = ROOT / "tools" / "coad-validator" / "src" / "coad_validator" / "schema"
    root_schema_paths = sorted(SCHEMA_DIR.rglob("*.json"))

    assert root_schema_paths
    for root_schema_path in root_schema_paths:
        relative_path = root_schema_path.relative_to(SCHEMA_DIR)
        bundled_schema_path = bundled_schema_dir / relative_path
        assert bundled_schema_path.is_file()
        assert bundled_schema_path.read_text(encoding="utf-8") == root_schema_path.read_text(encoding="utf-8")


def _run_json(args: list[str]) -> dict[str, Any]:
    result = subprocess.run(args, check=False, capture_output=True, text=True)
    return json.loads(result.stdout)


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    schema_path = REPORT_SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
