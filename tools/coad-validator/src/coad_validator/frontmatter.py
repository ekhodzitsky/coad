from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .model import ContractDocument, ValidationIssue

_DELIMITER = "---"


def read_contract(path: Path) -> tuple[ContractDocument | None, ValidationIssue | None]:
    text = path.read_text(encoding="utf-8")
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
    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", ".venv", "templates"} for part in path.parts):
            continue
        document, issue = read_contract(path)
        if issue is not None:
            issues.append(issue)
        if document is not None and document.kind.endswith("_contract"):
            documents.append(document)
    return documents, issues


def _normalize_mapping(value: dict[Any, Any]) -> dict[str, Any]:
    return {str(key): item for key, item in value.items()}
