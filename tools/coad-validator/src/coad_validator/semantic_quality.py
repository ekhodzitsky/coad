from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .model import ContractDocument, ValidationIssue
from .module_context import (
    REQUIRED_AGENT_CONTEXT_FILES,
    module_context_path,
    module_directory,
    resolve_contract_relative_path,
)

_ANGLE_PLACEHOLDER = re.compile(
    r"<[^>\n]*(?:todo|tbd|replace|module|name|path|target|command|proof|owner)[^>\n]*>",
    re.IGNORECASE,
)
_PLACEHOLDER_EXACT = {
    "...",
    "n/a",
    "na",
    "none",
    "replace me",
    "tbd",
    "to do",
    "todo",
    "your module",
    "your name",
    "your-name",
}
_PLACEHOLDER_FRAGMENTS = (
    "{{",
    "}}",
    "[todo]",
    "tbd:",
    "todo:",
    "lorem ipsum",
    "replace me",
    "your module",
    "your name",
    "your-name",
)
_GENERIC_PURPOSES = {
    "app",
    "code",
    "code module",
    "component",
    "module",
    "module for code",
    "service",
    "some code",
    "stuff",
    "system",
    "tbd",
    "thing",
    "todo",
    "tool",
    "utility",
}
_GENERIC_PURPOSE_WORDS = {
    "app",
    "code",
    "component",
    "module",
    "service",
    "stuff",
    "system",
    "thing",
    "tool",
    "utility",
}


def validate_semantic_quality(documents: list[ContractDocument], root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for document in documents:
        if document.kind != "module_contract":
            continue
        issues.extend(_validate_contract_text(document))
        issues.extend(_validate_surfaces(document))
        issues.extend(_validate_context_files(root, document))
        issues.extend(_validate_owned_paths(root, document))
    return issues


def _validate_contract_text(document: ContractDocument) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    purpose = _string(document.data.get("purpose"))
    if purpose is not None and _has_placeholder(purpose):
        issues.append(_issue(document, "semantic placeholder in module purpose", "semantic.placeholder"))
    if purpose is not None and _purpose_too_generic(purpose):
        issues.append(
            _issue(
                document,
                "module purpose is too generic for agent-safe editing",
                "semantic.purpose_too_generic",
            )
        )

    for field, value in _contract_strings(document.data):
        if _has_placeholder(value):
            issues.append(_issue(document, f"semantic placeholder in {field}", "semantic.placeholder"))
    return issues


def _validate_surfaces(document: ContractDocument) -> list[ValidationIssue]:
    surfaces = _dict_list(document.data.get("surface"))
    if not surfaces:
        return [
            _issue(
                document,
                "module contract must describe at least one editable surface",
                "semantic.surface_missing",
            )
        ]

    issues: list[ValidationIssue] = []
    for surface in surfaces:
        name = _string(surface.get("name"))
        if _string(surface.get("visibility")) == "public" and name and not _consumer_uses(document.data, name):
            issues.append(
                _issue(
                    document,
                    f"public surface has no declared consumer: {name}",
                    "semantic.public_surface_without_consumer",
                )
            )

        proof = surface.get("proof")
        if isinstance(proof, dict):
            issues.extend(_validate_proof(document, proof, f"surface {name or '<unnamed>'} proof"))

    for invariant in _dict_list(document.data.get("invariants")):
        proof = invariant.get("proof")
        if isinstance(proof, dict):
            invariant_id = _string(invariant.get("id")) or "<unnamed>"
            issues.extend(_validate_proof(document, proof, f"invariant {invariant_id} proof"))

    return issues


def _validate_proof(document: ContractDocument, proof: dict[str, Any], label: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for field in ("target", "command"):
        value = _string(proof.get(field))
        if value is not None and _has_placeholder(value):
            issues.append(_issue(document, f"semantic placeholder in {label} {field}", "semantic.proof_placeholder"))
    return issues


def _validate_context_files(root: Path, document: ContractDocument) -> list[ValidationIssue]:
    module = _string(document.data.get("module"))
    if not module:
        return []
    context_path = module_context_path(document, module)
    if context_path.is_absolute() or ".." in context_path.parts:
        return []
    directory = module_directory(root, document, context_path)
    if not directory.is_dir():
        return []

    issues: list[ValidationIssue] = []
    for filename in REQUIRED_AGENT_CONTEXT_FILES:
        path = directory / filename
        if path.is_file() and not _has_meaningful_context(path):
            issues.append(
                ValidationIssue(
                    path,
                    f"module agent context file has no meaningful guidance: {filename}",
                    code="semantic.context_file_empty",
                )
            )
    return issues


def _validate_owned_paths(root: Path, document: ContractDocument) -> list[ValidationIssue]:
    workcell = document.data.get("workcell")
    if not isinstance(workcell, dict):
        return []
    owns_paths = workcell.get("owns_paths")
    if not isinstance(owns_paths, list):
        return []

    issues: list[ValidationIssue] = []
    for raw_path in owns_paths:
        if not isinstance(raw_path, str) or not raw_path:
            continue
        owned_path = Path(raw_path)
        if owned_path.is_absolute() or ".." in owned_path.parts:
            continue
        target = resolve_contract_relative_path(root, document, owned_path)
        if not target.exists():
            issues.append(
                _issue(
                    document,
                    f"workcell owns_path does not exist: {raw_path}",
                    "semantic.owns_path_missing",
                )
            )
    return issues


def _contract_strings(data: dict[str, Any]) -> list[tuple[str, str]]:
    strings: list[tuple[str, str]] = []
    for index, owner in enumerate(_string_list(data.get("owners"))):
        strings.append((f"owners[{index}]", owner))

    for index, surface in enumerate(_dict_list(data.get("surface"))):
        for field in ("name", "signature", "contract"):
            value = _string(surface.get(field))
            if value is not None:
                strings.append((f"surface[{index}].{field}", value))

    dependencies = data.get("dependencies")
    if isinstance(dependencies, dict):
        for group in ("internal", "external"):
            for index, dependency in enumerate(_dict_list(dependencies.get(group))):
                for field in ("module", "name", "scope", "reason"):
                    value = _string(dependency.get(field))
                    if value is not None:
                        strings.append((f"dependencies.{group}[{index}].{field}", value))

    for index, consumer in enumerate(_dict_list(data.get("consumers"))):
        path = _string(consumer.get("path"))
        if path is not None:
            strings.append((f"consumers[{index}].path", path))
        for use_index, use in enumerate(_string_list(consumer.get("uses"))):
            strings.append((f"consumers[{index}].uses[{use_index}]", use))

    for index, invariant in enumerate(_dict_list(data.get("invariants"))):
        for field in ("id", "rule"):
            value = _string(invariant.get(field))
            if value is not None:
                strings.append((f"invariants[{index}].{field}", value))

    return strings


def _has_placeholder(value: str) -> bool:
    normalized = _normalize_text(value)
    if normalized in _PLACEHOLDER_EXACT:
        return True
    return _ANGLE_PLACEHOLDER.search(value) is not None or any(
        fragment in normalized for fragment in _PLACEHOLDER_FRAGMENTS
    )


def _purpose_too_generic(value: str) -> bool:
    normalized = _normalize_text(value)
    if normalized in _GENERIC_PURPOSES:
        return True
    words = re.findall(r"[a-z0-9]+", normalized)
    return bool(words) and len(words) <= 3 and all(word in _GENERIC_PURPOSE_WORDS for word in words)


def _consumer_uses(data: dict[str, Any], surface_name: str) -> bool:
    for consumer in _dict_list(data.get("consumers")):
        if surface_name in _string_list(consumer.get("uses")):
            return True
    return False


def _has_meaningful_context(path: Path) -> bool:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return False
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped in {"---", "..."}:
            continue
        if stripped.startswith("#"):
            continue
        if _normalize_text(stripped) in _PLACEHOLDER_EXACT:
            continue
        return True
    return False


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _string(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _string_list(value: object) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _dict_list(value: object) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _issue(document: ContractDocument, message: str, code: str) -> ValidationIssue:
    return ValidationIssue(document.path, message, code=code)
