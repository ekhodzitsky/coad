from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .model import ContractDocument, ValidationIssue

_SCHEMA_BY_KIND = {
    "goal_contract": "goal-contract.schema.json",
    "module_contract": "module-contract.schema.json",
    "task_contract": "task-contract.schema.json",
    "proof_contract": "proof-contract.schema.json",
    "handoff_contract": "handoff-contract.schema.json",
    "review_contract": "review-contract.schema.json",
    "integration_contract": "integration-contract.schema.json",
}


def validate_schemas(
    documents: list[ContractDocument], schema_dir: Path
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    validators: dict[str, Draft202012Validator] = {}

    for document in documents:
        schema_name = _SCHEMA_BY_KIND.get(document.kind)
        if schema_name is None:
            issues.append(document_issue(document, f"unknown contract kind: {document.kind}"))
            continue

        validator = validators.get(schema_name)
        if validator is None:
            schema_path = schema_dir / schema_name
            if not schema_path.exists():
                issues.append(document_issue(document, f"schema not found: {schema_name}"))
                continue
            schema = _read_json(schema_path)
            validator = Draft202012Validator(schema)
            validators[schema_name] = validator

        for error in sorted(validator.iter_errors(document.data), key=str):
            location = ".".join(str(part) for part in error.absolute_path)
            prefix = f"schema violation at {location}: " if location else "schema violation: "
            issues.append(document_issue(document, prefix + error.message))

    return issues


def document_issue(document: ContractDocument, message: str) -> ValidationIssue:
    return ValidationIssue(document.path, message)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
