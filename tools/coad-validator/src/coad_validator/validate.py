from __future__ import annotations

from pathlib import Path

from .frontmatter import discover_contracts
from .graph import validate_graph
from .lease_manifest import validate_lease_manifest
from .model import ContractDocument, ValidationFailure, ValidationIssue
from .module_context import validate_module_context
from .release_metadata import validate_release_metadata
from .schema import validate_schemas
from .semantic_quality import validate_semantic_quality
from .workcell_budget import validate_workcell_budgets
from .workcell_graph import validate_workcell_graph


class ValidationReport:
    def __init__(self, root: Path, documents: list[ContractDocument], issues: list[ValidationIssue]) -> None:
        self.root = root
        self.documents = documents
        self.issues = issues

    @property
    def ok(self) -> bool:
        return not self.issues

    def raise_if_failed(self) -> None:
        if self.issues:
            raise ValidationFailure(self.issues)


def validate_path(root: Path, schema_dir: Path | None = None, check_graph: bool = True) -> ValidationReport:
    resolved_root = root.resolve()
    resolved_schema_dir = (schema_dir or find_schema_dir(resolved_root)).resolve()

    documents, issues = discover_contracts(resolved_root)
    issues.extend(validate_schemas(documents, resolved_schema_dir))
    issues.extend(validate_module_context(documents, resolved_root))
    issues.extend(validate_workcell_budgets(documents, resolved_root))
    issues.extend(validate_workcell_graph(documents, resolved_root))
    issues.extend(validate_lease_manifest(documents, resolved_root, resolved_schema_dir))
    issues.extend(validate_semantic_quality(documents, resolved_root))
    issues.extend(validate_release_metadata(resolved_root))
    if check_graph:
        issues.extend(validate_graph(documents))

    return ValidationReport(resolved_root, documents, issues)


def find_schema_dir(start: Path) -> Path:
    candidates = [start]
    candidates.extend(start.parents)
    for candidate in candidates:
        schema_dir = candidate / "schema"
        if schema_dir.is_dir():
            return schema_dir
    bundled_schema_dir = Path(__file__).resolve().parent / "schema"
    if bundled_schema_dir.is_dir():
        return bundled_schema_dir
    raise FileNotFoundError(f"could not find schema directory from {start}")
