from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .frontmatter import read_contract
from .handoff_integrity import git_diff_for_root
from .report import versioned_report

if TYPE_CHECKING:
    from .validate import ValidationReport


ROOT_METHODOLOGY_DOCS = {
    "ADOPTION.md",
    "AGENT_FLOW.md",
    "AGENT_ONBOARDING.md",
    "COAD_PROJECT_STANDARD.md",
    "GETTING_STARTED.md",
    "GLOSSARY.md",
    "PRINCIPLES.md",
    "README.md",
    "SPEC.md",
}


@dataclass(frozen=True)
class ContractUpdate:
    path: str
    reason: str


def build_contract_update_integrity_report(
    root: Path,
    _schema_dir: Path | None = None,
    _contract_report: ValidationReport | None = None,
) -> dict[str, Any]:
    resolved_root = root.resolve()
    handoff_path = resolved_root / "HANDOFF.md"
    if not handoff_path.is_file():
        return _skipped("missing_handoff", "HANDOFF.md was not found")

    handoff, issue = read_contract(handoff_path)
    if issue is not None:
        return _result(False, "violation", "", [], [], [_issue(issue.code, "HANDOFF.md", issue.message)])
    if handoff is None or handoff.kind != "handoff_contract":
        return _result(
            False,
            "violation",
            "",
            [],
            [],
            [_issue("handoff.invalid", "HANDOFF.md", "HANDOFF.md is not a handoff_contract")],
        )

    diff, skip_reason = git_diff_for_root(resolved_root)
    if skip_reason is not None:
        return _skipped(skip_reason[0], skip_reason[1])
    assert diff is not None

    changed_files = [path for path in diff.changed_files if path != "HANDOFF.md"]
    if not changed_files:
        return _skipped("no_changed_files", "git diff has no changed files for this COAD root", diff.base)

    methodology_files = sorted(path for path in changed_files if _is_methodology_file(path))
    updates = _contract_updates(handoff.data.get("contract_updates"))
    issues = [
        *_missing_update_issues(methodology_files, updates),
        *_empty_reason_issues(updates),
        *_extra_update_warnings(changed_files, updates),
    ]
    has_errors = any(issue["severity"] == "error" for issue in issues)
    status = "violation" if has_errors else "warning" if issues else "pass"
    return _result(
        not has_errors,
        status,
        diff.base,
        methodology_files,
        updates,
        issues,
    )


def _contract_updates(value: object) -> list[ContractUpdate]:
    if not isinstance(value, list):
        return []
    updates: list[ContractUpdate] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if not isinstance(path, str) or not path:
            continue
        reason = item.get("reason")
        updates.append(ContractUpdate(path=path, reason=reason if isinstance(reason, str) else ""))
    return updates


def _missing_update_issues(
    methodology_files: list[str],
    updates: list[ContractUpdate],
) -> list[dict[str, str]]:
    updated_paths = {update.path for update in updates}
    return [
        _issue(
            "contract_update.missing",
            path,
            f"changed methodology file is missing from HANDOFF.contract_updates: {path}",
        )
        for path in methodology_files
        if path not in updated_paths
    ]


def _empty_reason_issues(updates: list[ContractUpdate]) -> list[dict[str, str]]:
    return [
        _issue(
            "contract_update.empty_reason",
            update.path,
            f"HANDOFF.contract_updates entry for {update.path} must include a non-empty reason",
        )
        for update in updates
        if not update.reason.strip()
    ]


def _extra_update_warnings(
    changed_files: list[str],
    updates: list[ContractUpdate],
) -> list[dict[str, str]]:
    changed = set(changed_files)
    return [
        _issue(
            "contract_update.extra",
            update.path,
            f"HANDOFF.contract_updates lists a file not changed in git diff: {update.path}",
            severity="warning",
        )
        for update in updates
        if update.path not in changed
    ]


def _is_methodology_file(path: str) -> bool:
    name = Path(path).name
    if name in {"HANDOFF.md", "README.md", "TODO.md"} and "/" in path:
        return False
    if name.endswith("_CONTRACT.md") or name in {"MODULE_CONTRACT.md", "PROOF.md", "REVIEW.md", "INTEGRATION.md"}:
        return True
    if path in ROOT_METHODOLOGY_DOCS:
        return True
    if path.startswith("contracts/") and path.endswith(".md"):
        return True
    if path.startswith("project-contracts/") and path.endswith(".md"):
        return True
    if path.startswith("docs/") and path.endswith(".md"):
        return True
    if path.startswith("schema/") and path.endswith(".json"):
        return True
    if path.startswith("tools/coad-validator/src/coad_validator/schema/") and path.endswith(".json"):
        return True
    return False


def _skipped(reason: str, message: str, base: str = "") -> dict[str, Any]:
    return versioned_report(
        {
            "ok": True,
            "status": "skipped",
            "base": base,
            "changed_methodology_files": [],
            "contract_updates": [],
            "skip_reason": reason,
            "issues": [_issue("contract_update.skipped", "HANDOFF.md", message, severity="info")],
        }
    )


def _result(
    ok: bool,
    status: str,
    base: str,
    methodology_files: list[str],
    updates: list[ContractUpdate],
    issues: list[dict[str, str]],
) -> dict[str, Any]:
    return versioned_report(
        {
            "ok": ok,
            "status": status,
            "base": base,
            "changed_methodology_files": methodology_files,
            "contract_updates": [
                {
                    "path": update.path,
                    "reason": update.reason,
                }
                for update in updates
            ],
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
