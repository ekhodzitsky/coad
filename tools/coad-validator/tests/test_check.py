from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import coad_validator.graph_report as graph_report_module
import coad_validator.ledger as ledger_module
import coad_validator.policy as policy_module
import coad_validator.proof_matrix as proof_matrix_module
import coad_validator.proof_result_integrity as proof_result_integrity_module
import coad_validator.report_sources as report_sources_module
import coad_validator.schedule as schedule_module
import coad_validator.status as status_module
import coad_validator.task_scope_integrity as task_scope_integrity_module
from coad_validator import check as check_module
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
        "ledger-handoff-integrity",
        "policy-report",
        "handoff-integrity",
        "task-scope-integrity",
        "proof-result-integrity",
        "contract-update-integrity",
        "proof-artifact-integrity",
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


def test_check_report_requires_at_least_one_module_contract(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text(
        "Use COAD, run coad check ., and maintain MODULE_CONTRACT files.\n",
        encoding="utf-8",
    )

    payload = build_check_report(tmp_path, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert payload["status"] == "fail"
    assert {
        "code": "validation.module_contract_missing",
        "severity": "error",
        "path": "MODULE_CONTRACT.md",
        "message": "validation-report: missing at least one module_contract",
    } in payload["issues"]
    _assert_matches_report_schema("check-report.schema.json", payload)


def test_check_report_reports_invalid_utf8_markdown_without_crashing(tmp_path: Path) -> None:
    target = tmp_path / "onboarding"
    shutil.copytree(ONBOARDING_FIXTURE, target)
    (target / "bad.md").write_bytes(b"\xff")

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert {
        "code": "frontmatter.read_failed",
        "severity": "error",
        "path": "bad.md",
        "message": "validation-report: markdown file could not be read as UTF-8",
    } in payload["issues"]
    _assert_matches_report_schema("check-report.schema.json", payload)


def test_check_report_reports_invalid_utf8_agents_guidance_without_crashing(tmp_path: Path) -> None:
    target = tmp_path / "onboarding"
    shutil.copytree(ONBOARDING_FIXTURE, target)
    (target / "AGENTS.md").write_bytes(b"\xff")

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert {
        "code": "agent-guidance.failed",
        "severity": "error",
        "path": "AGENTS.md",
        "message": "agent-guidance: AGENTS.md could not be read as UTF-8",
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


def test_check_report_skips_handoff_integrity_without_git_context(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    handoff_check = _check(payload, "handoff-integrity")
    assert handoff_check["ok"] is True
    assert handoff_check["status"] == "skipped"
    task_scope_check = _check(payload, "task-scope-integrity")
    assert task_scope_check["ok"] is True
    assert task_scope_check["status"] == "skipped"
    proof_result_check = _check(payload, "proof-result-integrity")
    assert proof_result_check["ok"] is True
    assert proof_result_check["status"] == "pass"
    ledger_handoff_check = _check(payload, "ledger-handoff-integrity")
    assert ledger_handoff_check["ok"] is True
    assert ledger_handoff_check["status"] == "pass"
    contract_update_check = _check(payload, "contract-update-integrity")
    assert contract_update_check["ok"] is True
    assert contract_update_check["status"] == "skipped"
    proof_artifact_check = _check(payload, "proof-artifact-integrity")
    assert proof_artifact_check["ok"] is True
    assert proof_artifact_check["status"] == "pass"


def test_check_report_passes_when_handoff_changed_files_match_git_diff(tmp_path: Path) -> None:
    target = _git_repo_from_minimal_example(tmp_path)
    _write(target / "checkout" / "checkout_service.py", "def checkout():\n    return 'ok'\n")
    _write(target / "checkout" / "test_checkout_service.py", "def test_checkout():\n    assert True\n")

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    handoff_check = _check(payload, "handoff-integrity")
    assert handoff_check["ok"] is True
    assert handoff_check["status"] == "pass"
    task_scope_check = _check(payload, "task-scope-integrity")
    assert task_scope_check["ok"] is True
    assert task_scope_check["status"] == "pass"
    proof_result_check = _check(payload, "proof-result-integrity")
    assert proof_result_check["ok"] is True
    assert proof_result_check["status"] == "pass"
    ledger_handoff_check = _check(payload, "ledger-handoff-integrity")
    assert ledger_handoff_check["ok"] is True
    assert ledger_handoff_check["status"] == "pass"
    contract_update_check = _check(payload, "contract-update-integrity")
    assert contract_update_check["ok"] is True
    assert contract_update_check["status"] == "warning"
    proof_artifact_check = _check(payload, "proof-artifact-integrity")
    assert proof_artifact_check["ok"] is True
    assert proof_artifact_check["status"] == "pass"


def test_check_report_fails_when_handoff_changed_files_do_not_match_git_diff(tmp_path: Path) -> None:
    target = _git_repo_from_minimal_example(tmp_path)
    _write(target / "checkout" / "checkout_service.py", "def checkout():\n    return 'ok'\n")
    _write(target / "checkout" / "unlisted.py", "VALUE = 1\n")

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "handoff-integrity")["status"] == "mismatch"
    assert {
        "code": "handoff.changed_files_missing",
        "severity": "error",
        "path": "HANDOFF.md",
        "message": "handoff-integrity: changed file is not listed in handoff.changed_files: checkout/unlisted.py",
    } in payload["issues"]
    assert {
        "code": "handoff.changed_files_extra",
        "severity": "error",
        "path": "HANDOFF.md",
        "message": "handoff-integrity: handoff.changed_files lists a file not changed in git diff: checkout/test_checkout_service.py",
    } in payload["issues"]


def test_check_report_fails_when_git_diff_escapes_task_write_scope(tmp_path: Path) -> None:
    target = _git_repo_from_minimal_example(tmp_path)
    _replace_handoff_changed_files(target, ["checkout/checkout_service.py", "billing/discounts.py"])
    _write(target / "checkout" / "checkout_service.py", "def checkout():\n    return 'ok'\n")
    _write(target / "billing" / "discounts.py", "VALUE = 1\n")

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "handoff-integrity")["status"] == "pass"
    assert _check(payload, "task-scope-integrity")["status"] == "violation"
    assert {
        "code": "task_scope.write_scope_violation",
        "severity": "error",
        "path": "billing/discounts.py",
        "message": (
            "task-scope-integrity: changed file is outside TASK_CONTRACT.write_scope "
            "for checkout-negative-total-guard: billing/discounts.py"
        ),
    } in payload["issues"]


def test_check_report_fails_when_git_diff_hits_forbidden_mutation(tmp_path: Path) -> None:
    target = _git_repo_from_minimal_example(
        tmp_path,
        task_contract_replacements={
            "write_scope:\n  - checkout/**": "write_scope:\n  - checkout/**\n  - billing/**",
            "forbidden_mutations:\n  - change CheckoutDecision schema\n  - change pricing rules": "forbidden_mutations:\n  - billing/**",
        },
    )
    _replace_handoff_changed_files(target, ["billing/discounts.py"])
    _write(target / "billing" / "discounts.py", "VALUE = 1\n")

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "handoff-integrity")["status"] == "pass"
    assert _check(payload, "task-scope-integrity")["status"] == "violation"
    assert {
        "code": "task_scope.forbidden_mutation",
        "severity": "error",
        "path": "billing/discounts.py",
        "message": (
            "task-scope-integrity: changed file matches TASK_CONTRACT.forbidden_mutations "
            "for checkout-negative-total-guard: billing/discounts.py matches billing/**"
        ),
    } in payload["issues"]


def test_check_report_fails_when_handoff_omits_required_proof_result(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _replace_text(
        target / "HANDOFF.md",
        (
            "proof_results:\n"
            "  - command: test checkout.checkout_service.rejects_negative_total\n"
            "    status: pass\n"
            "  - command: test schemas/checkout-decision.schema.json\n"
            "    status: pass"
        ),
        (
            "proof_results:\n"
            "  - command: test schemas/checkout-decision.schema.json\n"
            "    status: pass"
        ),
    )

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-result-integrity")["status"] == "violation"
    assert {
        "code": "proof_result.handoff_missing",
        "severity": "error",
        "path": "HANDOFF.md",
        "message": (
            "proof-result-integrity: required proof command missing from "
            "HANDOFF.proof_results for checkout-negative-total-guard: "
            "test checkout.checkout_service.rejects_negative_total"
        ),
    } in payload["issues"]


def test_check_report_fails_when_handoff_proof_result_is_not_passing(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _replace_text(
        target / "HANDOFF.md",
        (
            "  - command: test checkout.checkout_service.rejects_negative_total\n"
            "    status: pass"
        ),
        (
            "  - command: test checkout.checkout_service.rejects_negative_total\n"
            "    status: fail"
        ),
    )

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-result-integrity")["status"] == "violation"
    assert {
        "code": "proof_result.handoff_not_passing",
        "severity": "error",
        "path": "HANDOFF.md",
        "message": (
            "proof-result-integrity: required proof command is not passing in "
            "HANDOFF.proof_results for checkout-negative-total-guard: "
            "test checkout.checkout_service.rejects_negative_total has status fail"
        ),
    } in payload["issues"]


def test_check_report_fails_when_ledger_proof_result_is_not_passing(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    ledger = _read_ledger(target)
    ledger["entries"][0]["proof_results"][0]["status"] = "fail"
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-result-integrity")["status"] == "violation"
    assert {
        "code": "proof_result.ledger_not_passing",
        "severity": "error",
        "path": "EXECUTION_LEDGER.json",
        "message": (
            "proof-result-integrity: required proof command is not passing in "
            "EXECUTION_LEDGER.json for checkout-negative-total-guard: "
            "test checkout.checkout_service.rejects_negative_total has status fail"
        ),
    } in payload["issues"]


def test_check_report_fails_when_ledger_entry_omits_handoff_path(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    ledger = _read_ledger(target)
    del ledger["entries"][0]["handoff_path"]
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "ledger-handoff-integrity")["status"] == "violation"
    assert {
        "code": "ledger_handoff.handoff_missing",
        "severity": "error",
        "path": "EXECUTION_LEDGER.json",
        "message": (
            "ledger-handoff-integrity: ledger entry must declare handoff_path "
            "for checkout-negative-total-guard"
        ),
    } in payload["issues"]


def test_check_report_fails_when_ledger_handoff_path_is_missing(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    ledger = _read_ledger(target)
    ledger["entries"][0]["handoff_path"] = "MISSING_HANDOFF.md"
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "ledger-handoff-integrity")["status"] == "violation"
    assert {
        "code": "ledger_handoff.handoff_not_found",
        "severity": "error",
        "path": "MISSING_HANDOFF.md",
        "message": "ledger-handoff-integrity: ledger handoff_path does not exist: MISSING_HANDOFF.md",
    } in payload["issues"]


def test_check_report_fails_when_ledger_handoff_path_escapes_root(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    ledger = _read_ledger(target)
    ledger["entries"][0]["handoff_path"] = "../HANDOFF.md"
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "ledger-handoff-integrity")["status"] == "violation"
    assert {
        "code": "ledger_handoff.path_escape",
        "severity": "error",
        "path": "../HANDOFF.md",
        "message": "ledger-handoff-integrity: ledger handoff_path escapes COAD root: ../HANDOFF.md",
    } in payload["issues"]


def test_check_report_fails_when_ledger_task_does_not_match_handoff(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _replace_text(
        target / "HANDOFF.md",
        "task_id: checkout-negative-total-guard",
        "task_id: different-task",
    )

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "ledger-handoff-integrity")["status"] == "violation"
    assert {
        "code": "ledger_handoff.task_mismatch",
        "severity": "error",
        "path": "HANDOFF.md",
        "message": (
            "ledger-handoff-integrity: ledger task_id checkout-negative-total-guard "
            "does not match HANDOFF.task_id different-task"
        ),
    } in payload["issues"]


def test_check_report_fails_when_ledger_changed_files_do_not_match_handoff(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    ledger = _read_ledger(target)
    ledger["entries"][0]["changed_files"] = ["artifacts/unit-test.txt", "checkout/unlisted.py"]
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "ledger-handoff-integrity")["status"] == "violation"
    assert {
        "code": "ledger_handoff.changed_files_missing",
        "severity": "error",
        "path": "EXECUTION_LEDGER.json",
        "message": (
            "ledger-handoff-integrity: handoff.changed_files is missing from "
            "ledger changed_files: TASK_CONTRACT.md"
        ),
    } in payload["issues"]
    assert {
        "code": "ledger_handoff.changed_files_extra",
        "severity": "error",
        "path": "EXECUTION_LEDGER.json",
        "message": (
            "ledger-handoff-integrity: ledger changed_files lists a file not "
            "in HANDOFF.changed_files: checkout/unlisted.py"
        ),
    } in payload["issues"]


def test_check_report_fails_when_completed_ledger_handoff_is_not_complete(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _replace_text(target / "HANDOFF.md", "status: complete", "status: pending")

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "ledger-handoff-integrity")["status"] == "violation"
    assert {
        "code": "ledger_handoff.status_mismatch",
        "severity": "error",
        "path": "HANDOFF.md",
        "message": (
            "ledger-handoff-integrity: completed ledger entry requires "
            "HANDOFF.status complete for checkout-negative-total-guard"
        ),
    } in payload["issues"]


def test_check_report_fails_when_passing_proof_result_omits_artifact(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _write_minimal_artifacts(target)
    ledger = _read_ledger(target)
    del ledger["entries"][0]["proof_results"][0]["artifact"]
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-artifact-integrity")["status"] == "violation"
    assert {
        "code": "proof_artifact.missing",
        "severity": "error",
        "path": "EXECUTION_LEDGER.json",
        "message": (
            "proof-artifact-integrity: passing proof result must declare an artifact: "
            "test checkout.checkout_service.rejects_negative_total"
        ),
    } in payload["issues"]


def test_check_report_fails_when_passing_proof_artifact_file_is_missing(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _write_minimal_artifacts(target)
    (target / "artifacts" / "unit-test.txt").unlink()

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-artifact-integrity")["status"] == "violation"
    assert {
        "code": "proof_artifact.missing",
        "severity": "error",
        "path": "artifacts/unit-test.txt",
        "message": "proof-artifact-integrity: proof artifact does not exist: artifacts/unit-test.txt",
    } in payload["issues"]


def test_check_report_fails_when_passing_proof_artifact_is_empty(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _write_minimal_artifacts(target, unit_text="")

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-artifact-integrity")["status"] == "violation"
    assert {
        "code": "proof_artifact.empty",
        "severity": "error",
        "path": "artifacts/unit-test.txt",
        "message": "proof-artifact-integrity: proof artifact is empty: artifacts/unit-test.txt",
    } in payload["issues"]


def test_check_report_fails_when_passing_proof_artifact_digest_is_missing(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _write_minimal_artifacts(target)
    ledger = _read_ledger(target)
    del ledger["entries"][0]["proof_results"][0]["artifact_sha256"]
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-artifact-integrity")["status"] == "violation"
    assert {
        "code": "proof_artifact.digest_missing",
        "severity": "error",
        "path": "EXECUTION_LEDGER.json",
        "message": (
            "proof-artifact-integrity: passing proof result must declare "
            "artifact_sha256: test checkout.checkout_service.rejects_negative_total "
            "(expected d4102b3b69047a96c82dfb2e7ef1075d72e36ec4ca27607b65ff44f09e24dac7)"
        ),
    } in payload["issues"]


def test_check_report_fails_when_passing_proof_artifact_bytes_are_missing(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _write_minimal_artifacts(target)
    ledger = _read_ledger(target)
    del ledger["entries"][0]["proof_results"][0]["artifact_bytes"]
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-artifact-integrity")["status"] == "violation"
    assert {
        "code": "proof_artifact.bytes_missing",
        "severity": "error",
        "path": "EXECUTION_LEDGER.json",
        "message": (
            "proof-artifact-integrity: passing proof result must declare "
            "artifact_bytes: test checkout.checkout_service.rejects_negative_total "
            "(expected 22)"
        ),
    } in payload["issues"]


def test_check_report_fails_when_passing_proof_artifact_bytes_do_not_match(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _write_minimal_artifacts(target)
    ledger = _read_ledger(target)
    ledger["entries"][0]["proof_results"][0]["artifact_bytes"] = 999
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-artifact-integrity")["status"] == "violation"
    assert {
        "code": "proof_artifact.bytes_mismatch",
        "severity": "error",
        "path": "artifacts/unit-test.txt",
        "message": "proof-artifact-integrity: proof artifact size mismatch for artifacts/unit-test.txt: expected 999, got 22",
    } in payload["issues"]


def test_check_report_fails_when_passing_proof_artifact_digest_does_not_match(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _write_minimal_artifacts(target)
    ledger = _read_ledger(target)
    ledger["entries"][0]["proof_results"][0]["artifact_sha256"] = "0" * 64
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-artifact-integrity")["status"] == "violation"
    assert any(
        issue["code"] == "proof_artifact.digest_mismatch"
        and issue["path"] == "artifacts/unit-test.txt"
        and issue["message"].startswith(
            "proof-artifact-integrity: proof artifact sha256 mismatch for "
            "artifacts/unit-test.txt: expected 0000000000000000000000000000000000000000000000000000000000000000, got "
        )
        for issue in payload["issues"]
    )


def test_check_report_fails_when_proof_artifact_path_escapes_root(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _write_minimal_artifacts(target)
    ledger = _read_ledger(target)
    ledger["entries"][0]["proof_results"][0]["artifact"] = "../unit-test.txt"
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-artifact-integrity")["status"] == "violation"
    assert {
        "code": "proof_artifact.path_escape",
        "severity": "error",
        "path": "../unit-test.txt",
        "message": "proof-artifact-integrity: proof artifact path escapes COAD root: ../unit-test.txt",
    } in payload["issues"]


def test_check_report_ignores_missing_artifact_for_non_passing_extra_result(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _write_minimal_artifacts(target)
    ledger = _read_ledger(target)
    ledger["entries"][0]["proof_results"].append({"command": "test optional.diagnostic", "status": "fail"})
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert _check(payload, "proof-artifact-integrity")["status"] == "pass"


def test_check_report_validates_declared_artifact_for_non_passing_result(tmp_path: Path) -> None:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    _write_minimal_artifacts(target)
    ledger = _read_ledger(target)
    ledger["entries"][0]["proof_results"].append(
        {
            "command": "test optional.diagnostic",
            "status": "fail",
            "artifact": "artifacts/missing-diagnostic.txt",
        }
    )
    _write_ledger(target, ledger)

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "proof-artifact-integrity")["status"] == "violation"
    assert {
        "code": "proof_artifact.missing",
        "severity": "error",
        "path": "artifacts/missing-diagnostic.txt",
        "message": "proof-artifact-integrity: proof artifact does not exist: artifacts/missing-diagnostic.txt",
    } in payload["issues"]


def test_check_report_fails_when_contract_change_is_not_declared(tmp_path: Path) -> None:
    target = _git_repo_from_minimal_example(
        tmp_path,
        task_contract_replacements={
            "write_scope:\n  - checkout/**": "write_scope:\n  - checkout/**\n  - TASK_CONTRACT.md",
        },
    )
    _replace_handoff_changed_files(target, ["TASK_CONTRACT.md"])
    _replace_contract_updates(target, [])
    _replace_text(
        target / "TASK_CONTRACT.md",
        "acceptance:\n  - CheckoutService rejects negative totals before producing CheckoutDecision.",
        (
            "acceptance:\n"
            "  - CheckoutService rejects negative totals before producing CheckoutDecision.\n"
            "  - Contract updates must be declared."
        ),
    )

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "handoff-integrity")["status"] == "pass"
    assert _check(payload, "task-scope-integrity")["status"] == "pass"
    assert _check(payload, "contract-update-integrity")["status"] == "violation"
    assert {
        "code": "contract_update.missing",
        "severity": "error",
        "path": "TASK_CONTRACT.md",
        "message": (
            "contract-update-integrity: changed methodology file is missing "
            "from HANDOFF.contract_updates: TASK_CONTRACT.md"
        ),
    } in payload["issues"]


def test_check_report_fails_when_contract_update_reason_is_empty(tmp_path: Path) -> None:
    target = _git_repo_from_minimal_example(
        tmp_path,
        task_contract_replacements={
            "write_scope:\n  - checkout/**": "write_scope:\n  - checkout/**\n  - TASK_CONTRACT.md",
        },
    )
    _replace_handoff_changed_files(target, ["TASK_CONTRACT.md"])
    _replace_contract_updates(target, [("TASK_CONTRACT.md", "")])
    _replace_text(
        target / "TASK_CONTRACT.md",
        "acceptance:\n  - CheckoutService rejects negative totals before producing CheckoutDecision.",
        (
            "acceptance:\n"
            "  - CheckoutService rejects negative totals before producing CheckoutDecision.\n"
            "  - Empty update reasons are rejected."
        ),
    )

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is False
    assert _check(payload, "contract-update-integrity")["status"] == "violation"
    assert {
        "code": "contract_update.empty_reason",
        "severity": "error",
        "path": "TASK_CONTRACT.md",
        "message": (
            "contract-update-integrity: HANDOFF.contract_updates entry "
            "for TASK_CONTRACT.md must include a non-empty reason"
        ),
    } in payload["issues"]


def test_check_report_warns_when_contract_update_entry_is_not_changed(tmp_path: Path) -> None:
    target = _git_repo_from_minimal_example(tmp_path)
    _write(target / "checkout" / "checkout_service.py", "def checkout():\n    return 'ok'\n")
    _write(target / "checkout" / "test_checkout_service.py", "def test_checkout():\n    assert True\n")

    payload = build_check_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    contract_update_check = _check(payload, "contract-update-integrity")
    assert contract_update_check["ok"] is True
    assert contract_update_check["status"] == "warning"


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


def test_coad_check_reuses_validation_report_for_internal_sources(monkeypatch: Any) -> None:
    calls = 0
    original_validate_path = check_module.validate_path

    def counting_validate_path(*args: Any, **kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        return original_validate_path(*args, **kwargs)

    def fail_revalidation(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("coad check source builder revalidated contracts")

    monkeypatch.setattr(check_module, "validate_path", counting_validate_path)
    for module in (
        graph_report_module,
        ledger_module,
        policy_module,
        proof_matrix_module,
        proof_result_integrity_module,
        report_sources_module,
        schedule_module,
        status_module,
        task_scope_integrity_module,
    ):
        monkeypatch.setattr(module, "validate_path", fail_revalidation)

    payload = build_check_report(MINIMAL_EXAMPLE, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert calls == 1


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


def _check(payload: dict[str, Any], name: str) -> dict[str, Any]:
    matches = [check for check in payload["checks"] if check["name"] == name]
    assert len(matches) == 1
    return matches[0]


def _git_repo_from_minimal_example(
    tmp_path: Path,
    task_contract_replacements: dict[str, str] | None = None,
) -> Path:
    target = tmp_path / "minimal"
    shutil.copytree(MINIMAL_EXAMPLE, target)
    if task_contract_replacements is not None:
        for old, new in task_contract_replacements.items():
            _replace_text(target / "TASK_CONTRACT.md", old, new)
    _replace_handoff_changed_files(target, ["checkout/checkout_service.py", "checkout/test_checkout_service.py"])
    _git(target, "init")
    _git(target, "config", "user.email", "coad-test@example.invalid")
    _git(target, "config", "user.name", "COAD Test")
    _git(target, "add", ".")
    _git(target, "commit", "-m", "baseline")
    return target


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _replace_handoff_changed_files(root: Path, changed_files: list[str]) -> None:
    ledger_changed_files = list(changed_files)
    if (root / ".git").exists() and "EXECUTION_LEDGER.json" not in ledger_changed_files:
        ledger_changed_files.append("EXECUTION_LEDGER.json")
    replacement = "\n".join(f"  - {path}" for path in ledger_changed_files)
    _replace_frontmatter_block(root / "HANDOFF.md", "changed_files", f"changed_files:\n{replacement}")
    _replace_ledger_changed_files(root, ledger_changed_files)


def _replace_contract_updates(root: Path, updates: list[tuple[str, str]]) -> None:
    if updates:
        replacement = "\n".join(
            f"  - path: {path}\n    reason: {json.dumps(reason)}"
            for path, reason in updates
        )
    else:
        replacement = "[]"
    _replace_frontmatter_block(
        root / "HANDOFF.md",
        "contract_updates",
        f"contract_updates: {replacement}" if not updates else f"contract_updates:\n{replacement}",
    )


def _replace_text(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"missing fixture text in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def _replace_frontmatter_block(path: Path, key: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    marker = f"{key}:"
    start = text.find(marker)
    if start == -1:
        raise AssertionError(f"missing fixture key in {path}: {key!r}")
    search_from = start + len(marker)
    end = len(text)
    for candidate in ("\nproof_results:", "\ncontract_updates:", "\ndecisions:", "\nknown_gaps:"):
        candidate_start = text.find(candidate, search_from)
        if candidate_start != -1:
            end = min(end, candidate_start + 1)
    path.write_text(f"{text[:start]}{replacement}\n{text[end:]}", encoding="utf-8")


def _read_ledger(root: Path) -> dict[str, Any]:
    return json.loads((root / "EXECUTION_LEDGER.json").read_text(encoding="utf-8"))


def _write_ledger(root: Path, payload: dict[str, Any]) -> None:
    (root / "EXECUTION_LEDGER.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def _replace_ledger_changed_files(root: Path, changed_files: list[str]) -> None:
    ledger = _read_ledger(root)
    ledger["entries"][0]["changed_files"] = changed_files
    _write_ledger(root, ledger)


def _write_minimal_artifacts(
    root: Path,
    unit_text: str = "unit proof transcript\n",
    schema_text: str = "schema proof transcript\n",
) -> None:
    _write(root / "artifacts" / "unit-test.txt", unit_text)
    _write(root / "artifacts" / "schema-test.txt", schema_text)
    ledger = _read_ledger(root)
    proof_results = ledger["entries"][0]["proof_results"]
    _set_artifact_metadata(proof_results[0], unit_text)
    _set_artifact_metadata(proof_results[1], schema_text)
    _write_ledger(root, ledger)


def _set_artifact_metadata(proof_result: dict[str, Any], content: str) -> None:
    payload = content.encode("utf-8")
    proof_result["artifact_sha256"] = hashlib.sha256(payload).hexdigest()
    proof_result["artifact_bytes"] = len(payload)


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    schema_path = REPORT_SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
