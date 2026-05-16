from __future__ import annotations

from pathlib import Path

from .model import ContractDocument, ValidationIssue

REQUIRED_AGENT_CONTEXT_FILES = ("README.md", "TODO.md")


def validate_module_context(documents: list[ContractDocument], root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for document in documents:
        if document.kind != "module_contract":
            continue
        module = document.data.get("module")
        if not isinstance(module, str) or not module:
            continue
        module_path = Path(module)
        if module_path.is_absolute() or ".." in module_path.parts:
            issues.append(
                ValidationIssue(
                    document.path,
                    f"module path must be relative and stay inside the repository: {module}",
                )
            )
            continue
        directory = module_directory(root, document, module_path)
        if not directory.is_dir():
            issues.append(ValidationIssue(directory, f"module directory does not exist: {module}"))
            continue
        for filename in REQUIRED_AGENT_CONTEXT_FILES:
            expected = directory / filename
            if not expected.is_file():
                issues.append(ValidationIssue(expected, f"module agent context is missing {filename}"))
    return issues


def module_directory(root: Path, document: ContractDocument, module_path: Path) -> Path:
    root_candidate = root / module_path
    if root_candidate.exists():
        return root_candidate

    local_candidate = document.path.parent / module_path
    if local_candidate.exists():
        return local_candidate

    return root_candidate
