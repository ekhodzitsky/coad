from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .graph_index import ContractIndex
from .model import ContractDocument
from .report import versioned_report
from .validate import find_schema_dir, validate_path


@dataclass(frozen=True)
class LedgerIssue:
    path: Path
    message: str
    severity: str = "error"

    def to_json(self, root: Path) -> dict[str, str]:
        return {
            "severity": self.severity,
            "path": _relative_path(self.path, root),
            "message": self.message,
        }


def build_ledger_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    contract_report = validate_path(root, schema_dir=schema_dir)
    resolved_schema_dir = (schema_dir or find_schema_dir(contract_report.root)).resolve()
    if not contract_report.ok:
        return versioned_report(
            {
                "ok": False,
                "status": "invalid",
                "contracts": len(contract_report.documents),
                "ledgers": [],
                "issues": [issue.to_json(contract_report.root) for issue in contract_report.issues],
            }
        )

    index = ContractIndex.from_documents(contract_report.documents)
    issues: list[LedgerIssue] = []
    ledgers = [
        _ledger_payload(path, index, contract_report.root, resolved_schema_dir, issues)
        for path in _ledger_paths(contract_report.root)
    ]
    if not ledgers:
        issues.append(LedgerIssue(contract_report.root / "EXECUTION_LEDGER.json", "missing execution ledger"))

    return versioned_report(
        {
            "ok": not issues,
            "status": "verified" if not issues else "ledger_issues",
            "contracts": len(contract_report.documents),
            "ledgers": ledgers,
            "issues": [issue.to_json(contract_report.root) for issue in issues],
        }
    )


def _ledger_payload(
    path: Path,
    index: ContractIndex,
    root: Path,
    schema_dir: Path,
    issues: list[LedgerIssue],
) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(LedgerIssue(path, f"invalid execution ledger JSON: {exc.msg}"))
        return {
            "path": _relative_path(path, root),
            "run_id": "",
            "goal_id": "",
            "entries": [],
        }

    _validate_ledger_schema(path, payload, schema_dir, issues)
    if not isinstance(payload, dict):
        issues.append(LedgerIssue(path, "execution ledger must be a JSON object"))
        return {
            "path": _relative_path(path, root),
            "run_id": "",
            "goal_id": "",
            "entries": [],
        }

    goal_id = _string_value(payload.get("goal_id"))
    goal = index.by_kind.get("goal_contract", {}).get(goal_id)
    if goal is None:
        issues.append(LedgerIssue(path, f"ledger references missing goal contract: {goal_id}"))

    return {
        "path": _relative_path(path, root),
        "run_id": _string_value(payload.get("run_id")),
        "goal_id": goal_id,
        "entries": [
            _entry_payload(path, entry, index, goal, issues)
            for entry in _list_value(payload.get("entries"))
            if isinstance(entry, dict)
        ],
    }


def _entry_payload(
    path: Path,
    entry: dict[str, Any],
    index: ContractIndex,
    goal: ContractDocument | None,
    issues: list[LedgerIssue],
) -> dict[str, Any]:
    task_id = _string_value(entry.get("task_id"))
    status = _string_value(entry.get("status"))
    task = index.task(task_id)
    required_commands = _required_task_commands(task) if task is not None else []
    passing_commands = _passing_entry_commands(entry)

    if task is None:
        issues.append(LedgerIssue(path, f"ledger entry references missing task contract: {task_id}"))
    elif goal is not None and task not in index.goal_tasks(goal):
        issues.append(LedgerIssue(path, f"ledger entry task is not part of goal {goal.identifier}: {task_id}"))

    missing_commands = [
        command
        for command in required_commands
        if command not in passing_commands
    ]
    if status == "completed":
        for command in missing_commands:
            issues.append(LedgerIssue(path, f"completed task {task_id} missing passing proof command: {command}"))

    return {
        "event_id": _string_value(entry.get("event_id")),
        "task_id": task_id,
        "status": status,
        "agent_id": _string_value(entry.get("agent_id")),
        "role": _string_value(entry.get("role")),
        "wave": _int_value(entry.get("wave")),
        "required_proof_commands": required_commands,
        "passing_proof_commands": passing_commands,
        "proof_status": "complete" if not missing_commands else "incomplete",
    }


def _validate_ledger_schema(
    path: Path,
    payload: Any,
    schema_dir: Path,
    issues: list[LedgerIssue],
) -> None:
    schema_path = schema_dir / "execution-ledger.schema.json"
    if not schema_path.is_file():
        issues.append(LedgerIssue(schema_path, "missing execution ledger schema"))
        return
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(payload), key=str):
        location = ".".join(str(part) for part in error.absolute_path)
        prefix = f"ledger schema violation at {location}: " if location else "ledger schema violation: "
        issues.append(LedgerIssue(path, prefix + error.message))


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


def _passing_entry_commands(entry: dict[str, Any]) -> list[str]:
    commands: list[str] = []
    for proof_result in _list_value(entry.get("proof_results")):
        if not isinstance(proof_result, dict):
            continue
        command = proof_result.get("command")
        status = proof_result.get("status")
        if isinstance(command, str) and status == "pass":
            commands.append(command)
    return commands


def _list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_value(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _int_value(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
