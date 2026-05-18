from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .frontmatter import read_contract
from .report import versioned_report
from .text_io import read_utf8

if TYPE_CHECKING:
    from .validate import ValidationReport


@dataclass(frozen=True)
class LedgerHandoffEntry:
    ledger_path: str
    event_id: str
    task_id: str
    status: str
    handoff_path: str
    handoff_status: str
    changed_files: list[str]
    ok: bool


def build_ledger_handoff_integrity_report(
    root: Path,
    _schema_dir: Path | None = None,
    _contract_report: ValidationReport | None = None,
) -> dict[str, Any]:
    resolved_root = root.resolve()
    ledger_paths = _ledger_paths(resolved_root)
    if not ledger_paths:
        return _skipped("missing_ledger", "EXECUTION_LEDGER.json was not found")

    entries: list[LedgerHandoffEntry] = []
    issues: list[dict[str, str]] = []
    referenced_handoffs: set[Path] = set()
    for ledger_path in ledger_paths:
        payload = _ledger_payload(ledger_path, resolved_root, issues)
        if payload is None:
            continue
        _collect_ledger_entries(resolved_root, ledger_path, payload, entries, issues, referenced_handoffs)

    _collect_orphan_handoff_warnings(resolved_root, referenced_handoffs, issues)
    has_errors = any(issue["severity"] == "error" for issue in issues)
    status = "violation" if has_errors else "warning" if issues else "pass"
    return versioned_report(
        {
            "ok": not has_errors,
            "status": status,
            "entries": [_entry_payload(entry) for entry in entries],
            "issues": issues,
        }
    )


def _collect_ledger_entries(
    root: Path,
    ledger_path: Path,
    payload: dict[str, Any],
    entries: list[LedgerHandoffEntry],
    issues: list[dict[str, str]],
    referenced_handoffs: set[Path],
) -> None:
    ledger_display = _relative_path(ledger_path, root)
    for entry in _list_value(payload.get("entries")):
        if not isinstance(entry, dict):
            continue
        issue_count = len(issues)
        event_id = _string_value(entry.get("event_id"))
        task_id = _string_value(entry.get("task_id"))
        status = _string_value(entry.get("status"), "unknown")
        ledger_changed_files = _string_list(entry.get("changed_files"))
        handoff_ref = _string_value(entry.get("handoff_path"))
        handoff_status = ""
        if not handoff_ref:
            issues.append(
                _issue(
                    "ledger_handoff.handoff_missing",
                    ledger_display,
                    f"ledger entry must declare handoff_path for {task_id}",
                )
            )
        else:
            handoff_path = _resolve_handoff_path(root, ledger_path.parent, handoff_ref, issues)
            if handoff_path is not None:
                referenced_handoffs.add(handoff_path.resolve())
                handoff_status = _validate_handoff(
                    root,
                    ledger_display,
                    handoff_path,
                    task_id,
                    status,
                    ledger_changed_files,
                    issues,
                )
        entries.append(
            LedgerHandoffEntry(
                ledger_path=ledger_display,
                event_id=event_id,
                task_id=task_id,
                status=status,
                handoff_path=handoff_ref,
                handoff_status=handoff_status,
                changed_files=ledger_changed_files,
                ok=len(issues) == issue_count,
            )
        )


def _resolve_handoff_path(
    root: Path,
    base_dir: Path,
    handoff_ref: str,
    issues: list[dict[str, str]],
) -> Path | None:
    candidate = Path(handoff_ref)
    if candidate.is_absolute() or ".." in candidate.parts:
        issues.append(
            _issue(
                "ledger_handoff.path_escape",
                handoff_ref,
                f"ledger handoff_path escapes COAD root: {handoff_ref}",
            )
        )
        return None

    handoff_path = base_dir / candidate
    try:
        handoff_path.resolve(strict=False).relative_to(root)
    except ValueError:
        issues.append(
            _issue(
                "ledger_handoff.path_escape",
                handoff_ref,
                f"ledger handoff_path escapes COAD root: {handoff_ref}",
            )
        )
        return None

    if not handoff_path.is_file():
        issues.append(
            _issue(
                "ledger_handoff.handoff_not_found",
                handoff_ref,
                f"ledger handoff_path does not exist: {handoff_ref}",
            )
        )
        return None
    return handoff_path


def _validate_handoff(
    root: Path,
    ledger_display: str,
    handoff_path: Path,
    ledger_task_id: str,
    ledger_status: str,
    ledger_changed_files: list[str],
    issues: list[dict[str, str]],
) -> str:
    display = _relative_path(handoff_path, root)
    handoff, read_issue = read_contract(handoff_path)
    if read_issue is not None:
        issues.append(_issue("ledger_handoff.handoff_invalid", display, read_issue.message))
        return ""
    if handoff is None or handoff.kind != "handoff_contract":
        issues.append(_issue("ledger_handoff.handoff_invalid", display, f"{display} is not a handoff_contract"))
        return ""

    handoff_task_id = _string_value(handoff.data.get("task_id"))
    handoff_status = _string_value(handoff.data.get("status"))
    if handoff_task_id != ledger_task_id:
        issues.append(
            _issue(
                "ledger_handoff.task_mismatch",
                display,
                f"ledger task_id {ledger_task_id} does not match HANDOFF.task_id {handoff_task_id}",
            )
        )
    if ledger_status == "completed" and handoff_status != "complete":
        issues.append(
            _issue(
                "ledger_handoff.status_mismatch",
                display,
                f"completed ledger entry requires HANDOFF.status complete for {ledger_task_id}",
            )
        )

    handoff_changed_files = _string_list(handoff.data.get("changed_files"))
    _compare_changed_files(ledger_display, ledger_changed_files, handoff_changed_files, issues)
    return handoff_status


def _compare_changed_files(
    ledger_display: str,
    ledger_changed_files: list[str],
    handoff_changed_files: list[str],
    issues: list[dict[str, str]],
) -> None:
    ledger_changed = set(ledger_changed_files)
    handoff_changed = set(handoff_changed_files)
    for path in sorted(handoff_changed - ledger_changed):
        issues.append(
            _issue(
                "ledger_handoff.changed_files_missing",
                ledger_display,
                f"handoff.changed_files is missing from ledger changed_files: {path}",
            )
        )
    for path in sorted(ledger_changed - handoff_changed):
        issues.append(
            _issue(
                "ledger_handoff.changed_files_extra",
                ledger_display,
                f"ledger changed_files lists a file not in HANDOFF.changed_files: {path}",
            )
        )


def _collect_orphan_handoff_warnings(
    root: Path,
    referenced_handoffs: set[Path],
    issues: list[dict[str, str]],
) -> None:
    for handoff_path in _handoff_paths(root):
        if handoff_path.resolve() in referenced_handoffs:
            continue
        issues.append(
            _issue(
                "ledger_handoff.orphan_handoff",
                _relative_path(handoff_path, root),
                f"handoff is not referenced by any execution ledger entry: {_relative_path(handoff_path, root)}",
                severity="warning",
            )
        )


def _ledger_payload(path: Path, root: Path, issues: list[dict[str, str]]) -> dict[str, Any] | None:
    text, read_error = read_utf8(path)
    display = _relative_path(path, root)
    if read_error is not None:
        issues.append(_issue("ledger_handoff.ledger_read_failed", display, f"execution ledger {read_error}"))
        return None
    try:
        payload = json.loads(text or "")
    except json.JSONDecodeError as exc:
        issues.append(_issue("ledger_handoff.ledger_invalid_json", display, f"invalid execution ledger JSON: {exc.msg}"))
        return None
    if not isinstance(payload, dict):
        issues.append(_issue("ledger_handoff.ledger_invalid", display, "execution ledger must be a JSON object"))
        return None
    return payload


def _ledger_paths(root: Path) -> list[Path]:
    return [path for path in sorted(root.rglob("EXECUTION_LEDGER.json")) if not _should_skip(path)]


def _handoff_paths(root: Path) -> list[Path]:
    return [path for path in sorted(root.rglob("HANDOFF.md")) if not _should_skip(path)]


def _should_skip(path: Path) -> bool:
    parts = path.parts
    if any(part in {".git", ".venv", "__pycache__", "templates"} for part in parts):
        return True
    return any(first == "tests" and second == "fixtures" for first, second in zip(parts, parts[1:]))


def _entry_payload(entry: LedgerHandoffEntry) -> dict[str, Any]:
    return {
        "ledger_path": entry.ledger_path,
        "event_id": entry.event_id,
        "task_id": entry.task_id,
        "status": entry.status,
        "handoff_path": entry.handoff_path,
        "handoff_status": entry.handoff_status,
        "changed_files": entry.changed_files,
        "ok": entry.ok,
    }


def _list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _string_value(value: object, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback


def _skipped(reason: str, message: str) -> dict[str, Any]:
    return versioned_report(
        {
            "ok": True,
            "status": "skipped",
            "entries": [],
            "skip_reason": reason,
            "issues": [_issue("ledger_handoff.skipped", "EXECUTION_LEDGER.json", message, severity="info")],
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
