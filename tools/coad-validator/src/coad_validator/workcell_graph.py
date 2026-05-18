from __future__ import annotations

from pathlib import Path
from typing import Any

from .model import ContractDocument, ValidationIssue
from .ownership import owned_paths


def validate_workcell_graph(documents: list[ContractDocument], root: Path) -> list[ValidationIssue]:
    module_documents = {
        document.identifier: document
        for document in documents
        if document.kind == "module_contract" and document.identifier
    }
    issues: list[ValidationIssue] = []

    for module, document in module_documents.items():
        workcell = _workcell(document)
        if workcell is None:
            continue

        parent = _parent(workcell)
        if parent is not None and parent not in module_documents:
            issues.append(
                ValidationIssue(
                    document.path,
                    f"workcell parent does not exist: {parent}",
                    code="workcell.parent_missing",
                )
            )

        children = _children(workcell)
        if _workcell_type(workcell) == "leaf" and children:
            issues.append(
                ValidationIssue(
                    document.path,
                    "leaf workcell must not declare children",
                    code="workcell.leaf_has_children",
                )
            )

        for child in children:
            child_document = module_documents.get(child)
            if child_document is None:
                issues.append(
                    ValidationIssue(
                        document.path,
                        f"workcell child does not exist: {child}",
                        code="workcell.child_missing",
                    )
                )
                continue
            child_workcell = _workcell(child_document)
            child_parent = _parent(child_workcell) if child_workcell is not None else None
            if child_parent != module:
                issues.append(
                    ValidationIssue(
                        document.path,
                        f"workcell child does not point back to parent: {child} parent={child_parent or '<none>'}",
                        code="workcell.child_parent_mismatch",
                    )
                )

        if _workcell_type(workcell) == "composite":
            issues.extend(_validate_composite_owned_paths(root, document, module_documents, module, children))

    issues.extend(_validate_leaf_owned_path_overlaps(root, module_documents))
    issues.extend(_validate_parent_cycles(module_documents))
    return issues


def _validate_parent_cycles(module_documents: dict[str, ContractDocument]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    reported: set[str] = set()
    for module, document in module_documents.items():
        seen: list[str] = []
        current: str | None = module
        while current is not None:
            if current in seen:
                cycle = seen[seen.index(current) :] + [current]
                key = " -> ".join(cycle)
                if key not in reported:
                    issues.append(
                        ValidationIssue(
                            document.path,
                            f"workcell parent cycle detected: {key}",
                            code="workcell.parent_cycle",
                        )
                    )
                    reported.add(key)
                break
            seen.append(current)
            current_document = module_documents.get(current)
            if current_document is None:
                break
            workcell = _workcell(current_document)
            current = _parent(workcell) if workcell is not None else None
    return issues


def _validate_composite_owned_paths(
    root: Path,
    document: ContractDocument,
    module_documents: dict[str, ContractDocument],
    module: str,
    children: list[str],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    parent_paths = _owned_paths(root, document)
    if not parent_paths:
        return issues

    for child in children:
        child_document = module_documents.get(child)
        if child_document is None:
            continue
        for parent_path in parent_paths:
            for child_path in _owned_paths(root, child_document):
                if _contains_path(parent_path, child_path):
                    issues.append(
                        ValidationIssue(
                            document.path,
                            "composite workcell owns child implementation path: "
                            f"{module} owns {_relative_path(parent_path, root)} used by {child}",
                            code="workcell.composite_owns_child_path",
                        )
                    )
                    return issues
    return issues


def _validate_leaf_owned_path_overlaps(
    root: Path,
    module_documents: dict[str, ContractDocument],
) -> list[ValidationIssue]:
    leaf_paths: list[tuple[str, ContractDocument, Path]] = []
    for module, document in module_documents.items():
        workcell = _workcell(document)
        if workcell is None or _workcell_type(workcell) != "leaf":
            continue
        for owned_path in _owned_paths(root, document):
            leaf_paths.append((module, document, owned_path))

    issues: list[ValidationIssue] = []
    for index, (left_module, left_document, left_path) in enumerate(leaf_paths):
        for right_module, _right_document, right_path in leaf_paths[index + 1 :]:
            if left_module == right_module:
                continue
            if _contains_path(left_path, right_path) or _contains_path(right_path, left_path):
                issues.append(
                    ValidationIssue(
                        left_document.path,
                        "workcell owns_path overlaps: "
                        f"{left_module} {_relative_path(left_path, root)} overlaps with "
                        f"{right_module} {_relative_path(right_path, root)}",
                        code="workcell.owns_path_overlap",
                    )
                )
                return issues
    return issues


def _owned_paths(root: Path, document: ContractDocument) -> list[Path]:
    return [entry.resolved for entry in owned_paths(root, document)]


def _contains_path(parent_path: Path, child_path: Path) -> bool:
    return child_path == parent_path or child_path.is_relative_to(parent_path)


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _workcell(document: ContractDocument) -> dict[str, Any] | None:
    value = document.data.get("workcell")
    return value if isinstance(value, dict) else None


def _workcell_type(workcell: dict[str, Any]) -> str:
    value = workcell.get("type")
    return value if isinstance(value, str) else ""


def _parent(workcell: dict[str, Any] | None) -> str | None:
    if workcell is None:
        return None
    value = workcell.get("parent")
    return value if isinstance(value, str) and value else None


def _children(workcell: dict[str, Any]) -> list[str]:
    value = workcell.get("children")
    if not isinstance(value, list):
        return []
    return [child for child in value if isinstance(child, str) and child]
