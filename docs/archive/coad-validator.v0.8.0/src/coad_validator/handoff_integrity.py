from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .frontmatter import read_contract
from .report import versioned_report

if TYPE_CHECKING:
    from .validate import ValidationReport


@dataclass(frozen=True)
class GitDiff:
    base: str
    changed_files: list[str]


def build_handoff_integrity_report(
    root: Path,
    _schema_dir: Path | None = None,
    _contract_report: ValidationReport | None = None,
) -> dict[str, Any]:
    resolved_root = root.resolve()
    handoff_path = resolved_root / "HANDOFF.md"
    if not handoff_path.is_file():
        return _skipped("missing_handoff", "HANDOFF.md was not found")

    document, issue = read_contract(handoff_path)
    if issue is not None:
        return _mismatch([_issue(issue.code, "HANDOFF.md", issue.message)], "", [])
    if document is None or document.kind != "handoff_contract":
        return _mismatch([_issue("handoff.invalid", "HANDOFF.md", "HANDOFF.md is not a handoff_contract")], "", [])

    diff, skip_reason = git_diff_for_root(resolved_root)
    if skip_reason is not None:
        return _skipped(skip_reason[0], skip_reason[1])
    assert diff is not None

    changed_files = [path for path in diff.changed_files if path != "HANDOFF.md"]
    if not changed_files:
        return _skipped("no_changed_files", "git diff has no changed files for this COAD root", diff.base)

    declared_files = _string_list(document.data.get("changed_files"))
    issues: list[dict[str, str]] = []
    for path in sorted(set(changed_files) - set(declared_files)):
        issues.append(_issue("handoff.changed_files_missing", "HANDOFF.md", f"changed file is not listed in handoff.changed_files: {path}"))
    for path in sorted(set(declared_files) - set(changed_files)):
        issues.append(_issue("handoff.changed_files_extra", "HANDOFF.md", f"handoff.changed_files lists a file not changed in git diff: {path}"))

    if issues:
        return _mismatch(issues, diff.base, changed_files)
    return versioned_report(
        {
            "ok": True,
            "status": "pass",
            "base": diff.base,
            "changed_files": changed_files,
            "issues": [],
        }
    )


def git_diff_for_root(root: Path) -> tuple[GitDiff | None, tuple[str, str] | None]:
    return _git_diff(root)


def _git_diff(root: Path) -> tuple[GitDiff | None, tuple[str, str] | None]:
    repo_root = _git_output(root, "rev-parse", "--show-toplevel")
    if repo_root is None:
        return None, ("not_git_repo", "not inside a git repository")
    git_root = Path(repo_root)
    scope = _relative_to(root, git_root)
    base = _merge_base(git_root) or _head_ref(git_root)
    if base is None:
        return None, ("no_git_base", "could not determine a git diff base")
    changed = set(_git_lines(git_root, "diff", "--name-only", base, "--", scope))
    changed.update(_git_lines(git_root, "ls-files", "--others", "--exclude-standard", "--", scope))
    relative_changed = sorted(_relative_to(git_root / path, root) for path in changed)
    return GitDiff(base=base, changed_files=relative_changed), None


def _merge_base(root: Path) -> str | None:
    for candidate in ("origin/main", "origin/master", "upstream/main", "upstream/master"):
        base = _git_output(root, "merge-base", "HEAD", candidate)
        if base:
            return base
    return None


def _head_ref(root: Path) -> str | None:
    return "HEAD" if _git_output(root, "rev-parse", "--verify", "HEAD") else None


def _git_lines(root: Path, *args: str) -> list[str]:
    output = _git_output(root, *args)
    if output is None:
        return []
    return [line for line in output.splitlines() if line]


def _git_output(root: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _skipped(reason: str, message: str, base: str = "") -> dict[str, Any]:
    return versioned_report(
        {
            "ok": True,
            "status": "skipped",
            "base": base,
            "changed_files": [],
            "skip_reason": reason,
            "issues": [_issue("handoff.skipped", "HANDOFF.md", message, severity="info")],
        }
    )


def _mismatch(issues: list[dict[str, str]], base: str, changed_files: list[str]) -> dict[str, Any]:
    return versioned_report(
        {
            "ok": False,
            "status": "mismatch",
            "base": base,
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


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _relative_to(path: Path, root: Path) -> str:
    try:
        value = path.resolve().relative_to(root.resolve())
    except ValueError:
        return str(path)
    return "." if not value.parts else str(value)
