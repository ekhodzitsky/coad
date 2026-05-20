from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .model import ContractDocument, ValidationIssue
from .module_context import resolve_contract_relative_path


@dataclass(frozen=True)
class OwnedPath:
    raw: str
    resolved: Path


def owned_paths(root: Path, document: ContractDocument) -> list[OwnedPath]:
    root = root.resolve()
    entries: list[OwnedPath] = []
    for raw_path in _raw_owned_paths(document):
        owned_path = Path(raw_path)
        if _is_invalid_relative_path(owned_path):
            continue
        resolved = resolve_contract_relative_path(root, document, owned_path).resolve()
        if not resolved.is_relative_to(root):
            continue
        entries.append(OwnedPath(raw=raw_path, resolved=resolved))
    return entries


def validate_owned_path_references(root: Path, document: ContractDocument) -> list[ValidationIssue]:
    root = root.resolve()
    issues: list[ValidationIssue] = []
    for raw_path in _raw_owned_paths(document):
        owned_path = Path(raw_path)
        if _is_invalid_relative_path(owned_path):
            issues.append(
                ValidationIssue(
                    document.path,
                    f"workcell owns_path must be relative and stay inside the repository: {raw_path}",
                    code="semantic.owns_path_invalid",
                )
            )
            continue

        target = resolve_contract_relative_path(root, document, owned_path)
        resolved = target.resolve()
        if not resolved.is_relative_to(root):
            issues.append(
                ValidationIssue(
                    document.path,
                    f"workcell owns_path resolves outside repository: {raw_path}",
                    code="semantic.owns_path_outside_repository",
                )
            )
            continue

        if not target.exists():
            issues.append(
                ValidationIssue(
                    document.path,
                    f"workcell owns_path does not exist: {raw_path}",
                    code="semantic.owns_path_missing",
                )
            )
    return issues


def _raw_owned_paths(document: ContractDocument) -> list[str]:
    workcell = document.data.get("workcell")
    if not isinstance(workcell, dict):
        return []
    owns_paths = workcell.get("owns_paths")
    if not isinstance(owns_paths, list):
        return []
    return [raw_path for raw_path in owns_paths if isinstance(raw_path, str) and raw_path]


def _is_invalid_relative_path(path: Path) -> bool:
    return path.is_absolute() or ".." in path.parts
