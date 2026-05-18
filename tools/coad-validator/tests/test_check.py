from __future__ import annotations

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
        "policy-report",
        "handoff-integrity",
        "task-scope-integrity",
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
    replacement = "\n".join(f"  - {path}" for path in changed_files)
    _replace_text(
        root / "HANDOFF.md",
        "changed_files:\n  - checkout/checkout_service.py\n  - checkout/test_checkout_service.py",
        f"changed_files:\n{replacement}",
    )


def _replace_text(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"missing fixture text in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def _assert_matches_report_schema(schema_name: str, payload: dict[str, Any]) -> None:
    schema_path = REPORT_SCHEMA_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
