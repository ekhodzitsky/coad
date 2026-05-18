from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .model import ContractDocument, ValidationIssue
from .text_io import read_utf8

_DELIMITER = "---"
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
    "templates",
}


def read_contract(path: Path) -> tuple[ContractDocument | None, ValidationIssue | None]:
    text, read_error = read_utf8(path)
    if read_error is not None:
        return None, ValidationIssue(
            path,
            f"markdown file {read_error}",
            code="frontmatter.read_failed",
        )
    if text is None:
        return None, None
    if not text.startswith(f"{_DELIMITER}\n"):
        return None, None

    end = text.find(f"\n{_DELIMITER}\n", len(_DELIMITER) + 1)
    if end == -1:
        return None, ValidationIssue(path, "frontmatter is missing closing delimiter")

    raw = text[len(_DELIMITER) + 1 : end]
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        return None, ValidationIssue(path, f"frontmatter YAML is invalid: {exc}")

    if not isinstance(data, dict):
        return None, ValidationIssue(path, "frontmatter must be a mapping")

    normalized = _normalize_mapping(data)
    return ContractDocument(path=path, data=normalized), None


def discover_contracts(root: Path) -> tuple[list[ContractDocument], list[ValidationIssue]]:
    documents: list[ContractDocument] = []
    issues: list[ValidationIssue] = []
    skip_test_fixtures = not _inside_test_fixtures(root)
    for path in sorted(root.rglob("*.md")):
        if _should_skip(path, skip_test_fixtures=skip_test_fixtures):
            continue
        document, issue = read_contract(path)
        if issue is not None:
            issues.append(issue)
        if document is not None and document.kind.endswith("_contract"):
            documents.append(document)
    return documents, issues


def _should_skip(path: Path, skip_test_fixtures: bool) -> bool:
    parts = path.parts
    if any(part in _SKIP_DIRS for part in parts):
        return True
    return skip_test_fixtures and _inside_test_fixtures(path)


def _inside_test_fixtures(path: Path) -> bool:
    parts = path.parts
    return any(first == "tests" and second == "fixtures" for first, second in zip(parts, parts[1:]))


def _normalize_mapping(value: dict[Any, Any]) -> dict[str, Any]:
    return {str(key): item for key, item in value.items()}
