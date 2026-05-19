from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coad_validator.artifact_export import export_artifacts
from coad_validator.attest import build_attestation_report
from coad_validator.check import build_check_report
from coad_validator.pack import PackFailure, build_context_pack
from coad_validator.report import versioned_report
from coad_validator.report_sources import ATTESTATION_SOURCES, CORE_METHODOLOGY_SOURCES, build_source_payload
from coad_validator.validate import validate_path

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
EXTENSION_SCHEMA_DIR = ROOT / "schema" / "extensions"
BUNDLED_SCHEMA_DIR = ROOT / "tools" / "coad-validator" / "src" / "coad_validator" / "schema"
FIXTURES = Path(__file__).parent / "fixtures"


def _schema_file(name: str) -> Path:
    primary = SCHEMA_DIR / name
    if primary.exists():
        return primary
    return EXTENSION_SCHEMA_DIR / name


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


def test_graph_json_output_matches_report_schema() -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.graph_report_cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ]
    )

    _assert_matches_report_schema("graph-report.schema.json", payload)


def test_proof_matrix_json_output_matches_report_schema() -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.proof_matrix_cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ]
    )

    _assert_matches_report_schema("proof-matrix.schema.json", payload)


def test_drift_json_output_matches_report_schema() -> None:
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "coad_validator.drift_cli",
            str(ROOT),
        ]
    )

    _assert_matches_report_schema("drift-report.schema.json", payload)


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


def test_report_builders_match_manifest_schemas(tmp_path: Path) -> None:
    validation_report = validate_path(ROOT, schema_dir=SCHEMA_DIR)
    cases = {
        "check-report": build_check_report(ROOT, schema_dir=SCHEMA_DIR),
        "attestation-report": build_attestation_report(ROOT, schema_dir=SCHEMA_DIR, contract_report=validation_report),
        "export-report": export_artifacts(ROOT, schema_dir=SCHEMA_DIR, output_dir=tmp_path / "coad-export"),
        "context-pack": build_context_pack(FIXTURES / "valid" / "minimal-graph", "checkout-negative-total-guard", schema_dir=SCHEMA_DIR),
        "pack-error": _pack_error_payload(),
    }
    cases.update(
        {
            source.name: build_source_payload(source, ROOT, SCHEMA_DIR, validation_report)
            for source in ATTESTATION_SOURCES
        }
    )

    assert set(cases) == set(_report_manifest())
    for report_name, payload in cases.items():
        _assert_matches_manifest_report(report_name, payload)


def test_negative_report_payloads_match_manifest_schemas(tmp_path: Path) -> None:
    root = FIXTURES / "invalid" / "missing-proof"
    validation_report = validate_path(root, schema_dir=SCHEMA_DIR)
    source_cases = {
        source.name: build_source_payload(source, root, SCHEMA_DIR, validation_report)
        for source in CORE_METHODOLOGY_SOURCES
        if source.name in {"validation-report", "status-report", "proof-matrix", "graph-report", "schedule-report", "ledger-report", "policy-report"}
    }
    cases = {
        "check-report": build_check_report(root, schema_dir=SCHEMA_DIR),
        "attestation-report": build_attestation_report(root, schema_dir=SCHEMA_DIR, contract_report=validation_report),
        "export-report": export_artifacts(root, schema_dir=SCHEMA_DIR, output_dir=tmp_path / "coad-export-invalid"),
        **source_cases,
    }

    assert all(payload["ok"] is False for payload in cases.values())
    for report_name, payload in cases.items():
        _assert_matches_manifest_report(report_name, payload)


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
    ledger_schema_path = _schema_file("execution-ledger.schema.json")
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger_schema = json.loads(ledger_schema_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(ledger_schema)
    Draft202012Validator(ledger_schema).validate(ledger)


def test_example_proof_artifacts_match_artifact_schema() -> None:
    artifact_schema_path = _schema_file("proof-artifact.schema.json")
    artifact_schema = json.loads(artifact_schema_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(artifact_schema)
    validator = Draft202012Validator(artifact_schema)
    for artifact_path in sorted((ROOT / "examples" / "minimal" / "artifacts").glob("*.json")):
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        validator.validate(artifact)


def test_conformance_profile_matches_profile_schema() -> None:
    profile_path = ROOT / "COAD_PROFILE.json"
    profile_schema_path = _schema_file("conformance-profile.schema.json")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    profile_schema = json.loads(profile_schema_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(profile_schema)
    Draft202012Validator(profile_schema).validate(profile)


def test_bundled_schemas_match_repository_schemas() -> None:
    root_schema_paths = sorted(SCHEMA_DIR.rglob("*.json"))

    assert root_schema_paths
    for root_schema_path in root_schema_paths:
        relative_path = root_schema_path.relative_to(SCHEMA_DIR)
        bundled_schema_path = BUNDLED_SCHEMA_DIR / relative_path
        assert bundled_schema_path.is_file()
        assert bundled_schema_path.read_text(encoding="utf-8") == root_schema_path.read_text(encoding="utf-8")


def _run_json(args: list[str]) -> dict[str, Any]:
    result = subprocess.run(args, check=False, capture_output=True, text=True)
    return json.loads(result.stdout)


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    matches = [
        report["name"]
        for report in _report_manifest().values()
        if Path(report["schema"]).name == schema_name
    ]
    assert matches
    _assert_matches_manifest_report(matches[0], payload)


def _assert_matches_manifest_report(report_name: str, payload: dict[str, Any]) -> None:
    manifest = _report_manifest()
    assert report_name in manifest
    relative_schema = Path(manifest[report_name]["schema"])
    schema_path = SCHEMA_DIR / relative_schema
    bundled_schema_path = BUNDLED_SCHEMA_DIR / relative_schema
    assert schema_path.is_file()
    assert bundled_schema_path.is_file()
    assert bundled_schema_path.read_text(encoding="utf-8") == schema_path.read_text(encoding="utf-8")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)


def _report_manifest() -> dict[str, dict[str, Any]]:
    manifest = json.loads((SCHEMA_DIR / "report-manifest.json").read_text(encoding="utf-8"))
    return {report["name"]: report for report in manifest["reports"]}


def _pack_error_payload() -> dict[str, Any]:
    try:
        build_context_pack(FIXTURES / "valid" / "minimal-graph", "missing-task", schema_dir=SCHEMA_DIR)
    except PackFailure as exc:
        return versioned_report({"ok": False, "error": str(exc)})
    raise AssertionError("expected context pack failure")
