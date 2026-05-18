from __future__ import annotations

from pathlib import Path
from typing import Any

from .model import ContractDocument, ValidationIssue
from .module_context import (
    module_context_path,
    module_directory,
)
from .ownership import owned_paths

_AGENT_CONTEXT_FILES = {"AGENTS.md", "MODULE_CONTRACT.md", "README.md", "TODO.md"}
_SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
}


def validate_workcell_budgets(documents: list[ContractDocument], root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for document in documents:
        if document.kind != "module_contract":
            continue

        workcell = document.data.get("workcell")
        if not isinstance(workcell, dict):
            continue
        budget = workcell.get("context_budget")
        if not isinstance(budget, dict):
            continue

        module = document.data.get("module")
        if not isinstance(module, str) or not module:
            continue
        context_path = module_context_path(document, module)
        if context_path.is_absolute() or ".." in context_path.parts:
            continue

        module_dir = module_directory(root, document, context_path)
        if not module_dir.exists():
            continue

        owned_files = _owned_files(root, document, workcell, module_dir)
        actuals = {
            "max_files": len(owned_files),
            "max_source_lines": _source_lines(owned_files),
            "max_contract_lines": _line_count(document.path),
            "max_readme_lines": _line_count(module_dir / "README.md"),
            "max_todo_lines": _line_count(module_dir / "TODO.md"),
            "max_surfaces": _list_len(document.data.get("surface")),
            "max_invariants": _list_len(document.data.get("invariants")),
        }

        issues.extend(_validate_budget_exceptions(document, workcell))
        for metric, actual in actuals.items():
            limit = budget.get(metric)
            if not isinstance(limit, int):
                continue
            if actual > limit and not _has_budget_exception(workcell, metric):
                issues.append(
                    ValidationIssue(
                        document.path,
                        f"workcell budget exceeded: {metric} actual {actual} > max {limit}",
                    )
                )
    return issues


def _owned_files(root: Path, document: ContractDocument, workcell: dict[str, Any], module_dir: Path) -> list[Path]:
    raw_paths = workcell.get("owns_paths")
    if not isinstance(raw_paths, list) or not raw_paths:
        return _walk_files(module_dir)

    files: list[Path] = []
    for entry in owned_paths(root, document):
        target = entry.resolved
        if target.is_file() and _is_counted_file(target):
            files.append(target)
        elif target.is_dir():
            files.extend(_walk_files(target))
    return sorted(set(files))


def _walk_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.rglob("*") if path.is_file() and _is_counted_file(path))


def _is_counted_file(path: Path) -> bool:
    return not any(part in _SKIP_DIRS for part in path.parts)


def _source_lines(files: list[Path]) -> int:
    return sum(_line_count(path) for path in files if path.name not in _AGENT_CONTEXT_FILES)


def _line_count(path: Path) -> int:
    if not path.is_file():
        return 0
    return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())


def _list_len(value: object) -> int:
    return len(value) if isinstance(value, list) else 0


def _validate_budget_exceptions(document: ContractDocument, workcell: dict[str, Any]) -> list[ValidationIssue]:
    exceptions = workcell.get("budget_exceptions")
    if exceptions is None:
        return []
    if not isinstance(exceptions, list):
        return [ValidationIssue(document.path, "workcell budget_exceptions must be a list")]

    issues: list[ValidationIssue] = []
    for exception in exceptions:
        if not isinstance(exception, dict):
            issues.append(ValidationIssue(document.path, "workcell budget exception must be a mapping"))
            continue
        reason = exception.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            issues.append(ValidationIssue(document.path, "workcell budget exception must include a reason"))
    return issues


def _has_budget_exception(workcell: dict[str, Any], metric: str) -> bool:
    exceptions = workcell.get("budget_exceptions")
    if not isinstance(exceptions, list):
        return False
    for exception in exceptions:
        if not isinstance(exception, dict):
            continue
        reason = exception.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            continue
        raw_metric = exception.get("metric", "context_budget")
        if raw_metric in {metric, "context_budget"}:
            return True
    return False
