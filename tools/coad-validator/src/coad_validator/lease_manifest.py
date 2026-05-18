from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from .model import ContractDocument, ValidationIssue
from .text_io import read_utf8
from .workcell_graph import _contains_path, _owned_paths, _workcell, _workcell_type

_LEASE_MANIFEST = Path(".coad") / "leases.yml"
_LEASE_SCHEMA = "lease-manifest.schema.json"


def validate_lease_manifest(
    documents: list[ContractDocument],
    root: Path,
    schema_dir: Path,
) -> list[ValidationIssue]:
    manifest_path = root / _LEASE_MANIFEST
    if not manifest_path.exists():
        return []

    issues: list[ValidationIssue] = []
    data = _read_manifest(manifest_path, issues)
    if data is None:
        return issues

    issues.extend(_validate_manifest_schema(manifest_path, data, schema_dir))
    if issues:
        return issues

    module_documents = {
        document.identifier: document
        for document in documents
        if document.kind == "module_contract" and document.identifier
    }
    write_leases: list[dict[str, Any]] = []

    for lease in data["leases"]:
        workcell = lease["workcell"]
        document = module_documents.get(workcell)
        if document is None:
            issues.append(
                ValidationIssue(
                    manifest_path,
                    f"lease references unknown workcell: {workcell}",
                    code="lease.workcell_unknown",
                )
            )
            continue

        if lease["mode"] != "write":
            continue

        workcell_type = _workcell_type(_workcell(document) or {})
        if workcell_type == "project":
            issues.append(
                ValidationIssue(
                    manifest_path,
                    f"project workcell cannot hold a write lease: {workcell}",
                    code="lease.project_write_forbidden",
                )
            )
            continue
        if workcell_type == "composite":
            issues.append(
                ValidationIssue(
                    manifest_path,
                    f"composite workcell cannot hold a write lease: {workcell}",
                    code="lease.composite_write_forbidden",
                )
            )
            continue

        scope_paths, scope_issues = _scope_paths(root, document, lease, manifest_path)
        issues.extend(scope_issues)
        owned_paths = _owned_paths(root, document)
        for scope_path in scope_paths:
            if not _inside_any_owned_path(scope_path, owned_paths):
                issues.append(
                    ValidationIssue(
                        manifest_path,
                        "lease scope is outside workcell ownership: "
                        f"{workcell} owns {_relative_path(scope_path, root)}",
                        code="lease.scope_outside_ownership",
                    )
                )
        write_leases.append({**lease, "scope_paths": scope_paths})

    issues.extend(_validate_write_conflicts(manifest_path, write_leases))
    return issues


def _read_manifest(path: Path, issues: list[ValidationIssue]) -> dict[str, Any] | None:
    text, read_error = read_utf8(path)
    if read_error is not None:
        issues.append(
            ValidationIssue(
                path,
                f"lease manifest {read_error}",
                code="lease.manifest_unreadable",
            )
        )
        return None
    if text is None:
        issues.append(
            ValidationIssue(
                path,
                "lease manifest could not be read",
                code="lease.manifest_unreadable",
            )
        )
        return None
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        issues.append(
            ValidationIssue(
                path,
                f"lease manifest YAML is invalid: {exc}",
                code="lease.yaml_invalid",
            )
        )
        return None
    if not isinstance(data, dict):
        issues.append(
            ValidationIssue(
                path,
                "lease manifest must be a mapping",
                code="lease.manifest_invalid",
            )
        )
        return None
    return data


def _validate_manifest_schema(
    path: Path,
    data: dict[str, Any],
    schema_dir: Path,
) -> list[ValidationIssue]:
    schema_path = schema_dir / _LEASE_SCHEMA
    if not schema_path.exists():
        return [
            ValidationIssue(
                schema_path,
                f"schema not found: {_LEASE_SCHEMA}",
                code="lease.schema_not_found",
            )
        ]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    issues: list[ValidationIssue] = []
    for error in sorted(validator.iter_errors(data), key=str):
        location = ".".join(str(part) for part in error.absolute_path)
        prefix = (
            f"lease schema violation at {location}: "
            if location
            else "lease schema violation: "
        )
        issues.append(
            ValidationIssue(
                path,
                prefix + error.message,
                code="lease.schema_violation",
            )
        )
    return issues


def _scope_paths(
    root: Path,
    document: ContractDocument,
    lease: dict[str, Any],
    manifest_path: Path,
) -> tuple[list[Path], list[ValidationIssue]]:
    scope = lease.get("scope")
    if not isinstance(scope, list) or not scope:
        return _owned_paths(root, document), []
    paths: list[Path] = []
    issues: list[ValidationIssue] = []
    for raw_path in scope:
        if not isinstance(raw_path, str):
            continue
        scope_path = Path(raw_path)
        if scope_path.is_absolute() or ".." in scope_path.parts:
            issues.append(
                ValidationIssue(
                    manifest_path,
                    f"lease scope must be relative and stay inside the repository: {raw_path}",
                    code="lease.scope_invalid",
                )
            )
            continue
        resolved = (root / scope_path).resolve()
        if not resolved.is_relative_to(root):
            issues.append(
                ValidationIssue(
                    manifest_path,
                    f"lease scope resolves outside repository: {raw_path}",
                    code="lease.scope_outside_repository",
                )
            )
            continue
        paths.append(resolved)
    return paths, issues


def _inside_any_owned_path(scope_path: Path, owned_paths: list[Path]) -> bool:
    return any(_contains_path(owned_path, scope_path) for owned_path in owned_paths)


def _validate_write_conflicts(
    manifest_path: Path,
    write_leases: list[dict[str, Any]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen_workcells: set[str] = set()
    for lease in write_leases:
        workcell = lease["workcell"]
        if workcell in seen_workcells:
            issues.append(
                ValidationIssue(
                    manifest_path,
                    f"multiple write leases for workcell: {workcell}",
                    code="lease.write_conflict",
                )
            )
        seen_workcells.add(workcell)

    for index, left in enumerate(write_leases):
        for right in write_leases[index + 1 :]:
            if left["workcell"] == right["workcell"]:
                continue
            if _scopes_overlap(left["scope_paths"], right["scope_paths"]):
                issues.append(
                    ValidationIssue(
                        manifest_path,
                        "write lease scopes overlap: "
                        f"{left['workcell']} overlaps with {right['workcell']}",
                        code="lease.write_conflict",
                    )
                )
                return issues
    return issues


def _scopes_overlap(left_paths: list[Path], right_paths: list[Path]) -> bool:
    for left_path in left_paths:
        for right_path in right_paths:
            if (
                _contains_path(left_path, right_path)
                or _contains_path(right_path, left_path)
            ):
                return True
    return False


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
