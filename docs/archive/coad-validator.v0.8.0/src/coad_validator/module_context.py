from __future__ import annotations

from pathlib import Path

from .model import ContractDocument, ValidationIssue

REQUIRED_AGENT_CONTEXT_FILES = ("README.md", "TODO.md")


def validate_module_context(documents: list[ContractDocument], root: Path) -> list[ValidationIssue]:
    root = root.resolve()
    issues: list[ValidationIssue] = []
    for document in documents:
        if document.kind != "module_contract":
            continue
        module = document.data.get("module")
        if not isinstance(module, str) or not module:
            continue
        context_path = module_context_path(document, module)
        if context_path.is_absolute() or ".." in context_path.parts:
            issues.append(
                ValidationIssue(
                    document.path,
                    f"module context path must be relative and stay inside the repository: {context_path}",
                )
            )
            continue
        directory = module_directory(root, document, context_path)
        if not directory.resolve().is_relative_to(root):
            issues.append(
                ValidationIssue(
                    document.path,
                    f"module context path resolves outside repository: {context_path}",
                    code="module.context_outside_repository",
                )
            )
            continue
        if not directory.is_dir():
            issues.append(ValidationIssue(directory, f"module directory does not exist: {module}"))
            continue
        for filename in REQUIRED_AGENT_CONTEXT_FILES:
            expected = directory / filename
            if not expected.is_file():
                issues.append(ValidationIssue(expected, f"module agent context is missing {filename}"))
    return issues


def module_directory(root: Path, document: ContractDocument, module_path: Path) -> Path:
    return resolve_contract_relative_path(root, document, module_path)


def module_context_path(document: ContractDocument, module: str) -> Path:
    workcell = document.data.get("workcell")
    if isinstance(workcell, dict):
        context_path = workcell.get("context_path")
        if isinstance(context_path, str) and context_path:
            return Path(context_path)
    return Path(module)


def resolve_contract_relative_path(root: Path, document: ContractDocument, path: Path) -> Path:
    root_candidate = root / path
    local_candidate = document.path.parent / path
    if _should_prefer_local_candidate(root, document, root_candidate, local_candidate):
        return local_candidate
    if root_candidate.exists():
        return root_candidate
    if local_candidate.exists():
        return local_candidate
    return root_candidate


def _should_prefer_local_candidate(
    root: Path,
    document: ContractDocument,
    root_candidate: Path,
    local_candidate: Path,
) -> bool:
    if document.path.parent == root or root_candidate == local_candidate or not local_candidate.exists():
        return False
    workcell = document.data.get("workcell")
    if isinstance(workcell, dict) and workcell.get("type") == "project":
        return False
    return True
