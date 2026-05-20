from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .frontmatter import read_contract
from .graph_index import ContractIndex
from .report import versioned_report
from .text_io import read_utf8
from .validate import validate_path

if TYPE_CHECKING:
    from .model import ContractDocument
    from .validate import ValidationReport


def build_proof_result_integrity_report(
    root: Path,
    schema_dir: Path | None = None,
    contract_report: ValidationReport | None = None,
) -> dict[str, Any]:
    resolved_root = root.resolve()
    handoff_path = resolved_root / "HANDOFF.md"
    if not handoff_path.is_file():
        return _skipped("missing_handoff", "HANDOFF.md was not found")

    handoff, issue = read_contract(handoff_path)
    if issue is not None:
        return _violation([_issue(issue.code, "HANDOFF.md", issue.message)], "", [], [], [])
    if handoff is None or handoff.kind != "handoff_contract":
        return _violation(
            [_issue("handoff.invalid", "HANDOFF.md", "HANDOFF.md is not a handoff_contract")],
            "",
            [],
            [],
            [],
        )

    task_id = _string_value(handoff.data.get("task_id"))
    if not task_id:
        return _skipped("missing_task_id", "HANDOFF.md does not declare task_id")

    task = _task_contract(resolved_root, schema_dir, contract_report, task_id)
    if task is None:
        return _violation(
            [
                _issue(
                    "proof_result.task_missing",
                    "HANDOFF.md",
                    f"task contract not found for task_id: {task_id}",
                )
            ],
            task_id,
            [],
            [],
            [],
        )

    required_commands = _required_task_commands(task)
    handoff_results = _proof_results_by_command(handoff.data.get("proof_results"))
    if not required_commands:
        return versioned_report(
            {
                "ok": True,
                "status": "pass",
                "task_id": task_id,
                "required_commands": [],
                "handoff_results": _result_entries(handoff_results, "HANDOFF.md"),
                "ledger_results": [],
                "issues": [],
            }
        )

    ledger_results, ledger_issues = _ledger_results_by_command(resolved_root, task_id)
    issues = [
        *ledger_issues,
        *_handoff_issues(task_id, required_commands, handoff_results),
        *_ledger_issues(task_id, required_commands, ledger_results),
    ]
    if issues:
        return _violation(
            issues,
            task_id,
            required_commands,
            _result_entries(handoff_results, "HANDOFF.md"),
            _ledger_entries(ledger_results),
        )
    return versioned_report(
        {
            "ok": True,
            "status": "pass",
            "task_id": task_id,
            "required_commands": required_commands,
            "handoff_results": _result_entries(handoff_results, "HANDOFF.md"),
            "ledger_results": _ledger_entries(ledger_results),
            "issues": [],
        }
    )


def _task_contract(
    root: Path,
    schema_dir: Path | None,
    contract_report: ValidationReport | None,
    task_id: str,
) -> ContractDocument | None:
    report = contract_report or validate_path(root, schema_dir=schema_dir)
    return ContractIndex.from_documents(report.documents).task(task_id)


def _required_task_commands(task: ContractDocument) -> list[str]:
    proof = task.data.get("proof")
    if not isinstance(proof, dict):
        return []
    required = proof.get("required")
    if not isinstance(required, list):
        return []
    commands: list[str] = []
    for item in required:
        if not isinstance(item, dict):
            continue
        command = item.get("command")
        if isinstance(command, str) and command:
            commands.append(command)
    return commands


def _handoff_issues(
    task_id: str,
    required_commands: list[str],
    handoff_results: dict[str, str],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for command in required_commands:
        status = handoff_results.get(command)
        if status is None:
            issues.append(
                _issue(
                    "proof_result.handoff_missing",
                    "HANDOFF.md",
                    f"required proof command missing from HANDOFF.proof_results for {task_id}: {command}",
                )
            )
        elif status != "pass":
            issues.append(
                _issue(
                    "proof_result.handoff_not_passing",
                    "HANDOFF.md",
                    f"required proof command is not passing in HANDOFF.proof_results for {task_id}: {command} has status {status}",
                )
            )
    return issues


def _ledger_issues(
    task_id: str,
    required_commands: list[str],
    ledger_results: dict[str, "LedgerCommandResult"],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for command in required_commands:
        result = ledger_results.get(command)
        if result is None:
            issues.append(
                _issue(
                    "proof_result.ledger_missing",
                    "EXECUTION_LEDGER.json",
                    f"required proof command missing from EXECUTION_LEDGER.json for {task_id}: {command}",
                )
            )
        elif result.status != "pass":
            issues.append(
                _issue(
                    "proof_result.ledger_not_passing",
                    result.path,
                    f"required proof command is not passing in EXECUTION_LEDGER.json for {task_id}: {command} has status {result.status}",
                )
            )
    return issues


@dataclass(frozen=True)
class LedgerCommandResult:
    status: str
    path: str


def _ledger_results_by_command(
    root: Path,
    task_id: str,
) -> tuple[dict[str, LedgerCommandResult], list[dict[str, str]]]:
    paths = _ledger_paths(root)
    if not paths:
        return {}, [_issue("proof_result.ledger_missing", "EXECUTION_LEDGER.json", "missing execution ledger")]

    results: dict[str, LedgerCommandResult] = {}
    issues: list[dict[str, str]] = []
    for path in paths:
        payload = _ledger_payload(path, root, issues)
        if payload is None:
            continue
        for entry in _list_value(payload.get("entries")):
            if not isinstance(entry, dict) or entry.get("task_id") != task_id:
                continue
            for proof_result in _list_value(entry.get("proof_results")):
                if not isinstance(proof_result, dict):
                    continue
                command = _string_value(proof_result.get("command"))
                status = _string_value(proof_result.get("status"), "unknown")
                if not command:
                    continue
                current = results.get(command)
                if current is None or current.status != "pass":
                    results[command] = LedgerCommandResult(status, _relative_path(path, root))
    return results, issues


def _ledger_payload(path: Path, root: Path, issues: list[dict[str, str]]) -> dict[str, Any] | None:
    text, read_error = read_utf8(path)
    if read_error is not None:
        issues.append(
            _issue(
                "proof_result.ledger_read_failed",
                _relative_path(path, root),
                f"execution ledger {read_error}",
            )
        )
        return None
    try:
        payload = json.loads(text or "")
    except json.JSONDecodeError as exc:
        issues.append(
            _issue(
                "proof_result.ledger_invalid_json",
                _relative_path(path, root),
                f"invalid execution ledger JSON: {exc.msg}",
            )
        )
        return None
    if not isinstance(payload, dict):
        issues.append(
            _issue(
                "proof_result.ledger_invalid",
                _relative_path(path, root),
                "execution ledger must be a JSON object",
            )
        )
        return None
    return payload


def _proof_results_by_command(value: object) -> dict[str, str]:
    results: dict[str, str] = {}
    for item in _list_value(value):
        if not isinstance(item, dict):
            continue
        command = _string_value(item.get("command"))
        if not command:
            continue
        status = _string_value(item.get("status"), "unknown")
        results[command] = status
    return results


def _result_entries(results: dict[str, str], source: str) -> list[dict[str, str]]:
    return [
        {
            "command": command,
            "status": status,
            "source": source,
        }
        for command, status in sorted(results.items())
    ]


def _ledger_entries(results: dict[str, LedgerCommandResult]) -> list[dict[str, str]]:
    return [
        {
            "command": command,
            "status": result.status,
            "source": result.path,
        }
        for command, result in sorted(results.items())
    ]


def _ledger_paths(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.rglob("EXECUTION_LEDGER.json"))
        if not _should_skip(path)
    ]


def _should_skip(path: Path) -> bool:
    parts = path.parts
    if any(part in {".git", ".venv", "__pycache__", "templates"} for part in parts):
        return True
    return any(first == "tests" and second == "fixtures" for first, second in zip(parts, parts[1:]))


def _list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_value(value: object, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback


def _skipped(reason: str, message: str, task_id: str = "") -> dict[str, Any]:
    return versioned_report(
        {
            "ok": True,
            "status": "skipped",
            "task_id": task_id,
            "required_commands": [],
            "handoff_results": [],
            "ledger_results": [],
            "skip_reason": reason,
            "issues": [_issue("proof_result.skipped", "HANDOFF.md", message, severity="info")],
        }
    )


def _violation(
    issues: list[dict[str, str]],
    task_id: str,
    required_commands: list[str],
    handoff_results: list[dict[str, str]],
    ledger_results: list[dict[str, str]],
) -> dict[str, Any]:
    return versioned_report(
        {
            "ok": False,
            "status": "violation",
            "task_id": task_id,
            "required_commands": required_commands,
            "handoff_results": handoff_results,
            "ledger_results": ledger_results,
            "issues": issues,
        }
    )


def _issue(code: str, path: str, message: str, severity: str = "error") -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "path": path,
        "message": message,
    }


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
