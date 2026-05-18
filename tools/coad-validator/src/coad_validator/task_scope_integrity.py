from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .frontmatter import read_contract
from .graph_index import ContractIndex, string_list
from .handoff_integrity import git_diff_for_root
from .report import versioned_report
from .validate import validate_path

if TYPE_CHECKING:
    from .model import ContractDocument
    from .validate import ValidationReport


def build_task_scope_integrity_report(
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
        return _violation([_issue(issue.code, "HANDOFF.md", issue.message)], "", "", [])
    if handoff is None or handoff.kind != "handoff_contract":
        return _violation(
            [_issue("handoff.invalid", "HANDOFF.md", "HANDOFF.md is not a handoff_contract")],
            "",
            "",
            [],
        )

    task_id = handoff.data.get("task_id")
    if not isinstance(task_id, str) or not task_id:
        return _skipped("missing_task_id", "HANDOFF.md does not declare task_id")

    diff, skip_reason = git_diff_for_root(resolved_root)
    if skip_reason is not None:
        return _skipped(skip_reason[0], skip_reason[1], task_id=task_id)
    assert diff is not None

    changed_files = [path for path in diff.changed_files if path != "HANDOFF.md"]
    if not changed_files:
        return _skipped(
            "no_changed_files",
            "git diff has no changed files for this COAD root",
            diff.base,
            task_id,
        )

    task = _task_contract(resolved_root, schema_dir, contract_report, task_id)
    if task is None:
        return _violation(
            [
                _issue(
                    "task_scope.task_missing",
                    "HANDOFF.md",
                    f"task contract not found for task_id: {task_id}",
                )
            ],
            diff.base,
            task_id,
            changed_files,
        )

    write_scope = string_list(task.data.get("write_scope"))
    forbidden_mutations = _path_like_scopes(string_list(task.data.get("forbidden_mutations")))
    issues = _scope_issues(task_id, changed_files, write_scope, forbidden_mutations)
    if issues:
        return _violation(issues, diff.base, task_id, changed_files)
    return versioned_report(
        {
            "ok": True,
            "status": "pass",
            "base": diff.base,
            "task_id": task_id,
            "changed_files": changed_files,
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


def _scope_issues(
    task_id: str,
    changed_files: list[str],
    write_scope: list[str],
    forbidden_mutations: list[str],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for path in changed_files:
        if not _matches_any(path, write_scope):
            issues.append(
                _issue(
                    "task_scope.write_scope_violation",
                    path,
                    f"changed file is outside TASK_CONTRACT.write_scope for {task_id}: {path}",
                )
            )
        forbidden_scope = _first_match(path, forbidden_mutations)
        if forbidden_scope is not None:
            issues.append(
                _issue(
                    "task_scope.forbidden_mutation",
                    path,
                    f"changed file matches TASK_CONTRACT.forbidden_mutations for {task_id}: {path} matches {forbidden_scope}",
                )
            )
    return issues


def _matches_any(path: str, scopes: list[str]) -> bool:
    return any(_scope_matches_path(scope, path) for scope in scopes)


def _first_match(path: str, scopes: list[str]) -> str | None:
    for scope in scopes:
        if _scope_matches_path(scope, path):
            return scope
    return None


def _scope_matches_path(scope: str, path: str) -> bool:
    if scope == path:
        return True
    tree_prefix = _tree_prefix(scope)
    if tree_prefix is not None:
        return path == tree_prefix or path.startswith(f"{tree_prefix}/")
    if any(character in scope for character in "*?["):
        return fnmatchcase(path, scope)
    if "/" not in scope and "." in scope:
        return path.rsplit("/", maxsplit=1)[-1] == scope
    return False


def _tree_prefix(scope: str) -> str | None:
    suffix = "/**"
    if not scope.endswith(suffix):
        return None
    return scope.removesuffix(suffix)


def _path_like_scopes(values: list[str]) -> list[str]:
    return [
        value
        for value in values
        if any(marker in value for marker in ("/", "*", "."))
    ]


def _skipped(reason: str, message: str, base: str = "", task_id: str = "") -> dict[str, Any]:
    return versioned_report(
        {
            "ok": True,
            "status": "skipped",
            "base": base,
            "task_id": task_id,
            "changed_files": [],
            "skip_reason": reason,
            "issues": [_issue("task_scope.skipped", "HANDOFF.md", message, severity="info")],
        }
    )


def _violation(
    issues: list[dict[str, str]],
    base: str,
    task_id: str,
    changed_files: list[str],
) -> dict[str, Any]:
    return versioned_report(
        {
            "ok": False,
            "status": "violation",
            "base": base,
            "task_id": task_id,
            "changed_files": changed_files,
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
