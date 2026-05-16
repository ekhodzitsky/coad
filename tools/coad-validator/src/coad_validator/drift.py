from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .report import versioned_report

REPORT_SCHEMAS = {
    "coad-validate": ["validation-report.schema.json"],
    "coad-status": ["status-report.schema.json"],
    "coad-proof-matrix": ["proof-matrix.schema.json"],
    "coad-graph": ["graph-report.schema.json"],
    "coad-pack": ["context-pack.schema.json", "pack-error.schema.json"],
}


@dataclass(frozen=True)
class DriftIssue:
    path: Path
    message: str
    severity: str = "error"

    def to_json(self, root: Path) -> dict[str, str]:
        return {
            "severity": self.severity,
            "path": _relative_path(self.path, root),
            "message": self.message,
        }


def build_drift_report(root: Path) -> dict[str, Any]:
    resolved_root = root.resolve()
    issues: list[DriftIssue] = []

    scripts = _tool_scripts(resolved_root, issues)
    tools_readme = _read_text(resolved_root / "tools" / "README.md", issues)
    validator_readme = _read_text(resolved_root / "tools" / "coad-validator" / "README.md", issues)
    validator_docs = _read_text(resolved_root / "docs" / "validator.md", issues)
    tool_schema_docs = _read_text(resolved_root / "docs" / "tool-output-schemas.md", issues)
    workflow = _read_text(resolved_root / ".github" / "workflows" / "ci.yml", issues)
    manifest_reports = _report_manifest(resolved_root, issues)
    manifest_schemas = {
        report["schema"]
        for report in manifest_reports
        if isinstance(report.get("schema"), str)
    }
    manifest_producers = {
        (report.get("producer"), report.get("schema"))
        for report in manifest_reports
        if isinstance(report.get("producer"), str) and isinstance(report.get("schema"), str)
    }

    for script in scripts:
        _require_text(script, resolved_root / "tools" / "README.md", tools_readme, issues, f"missing documented tool: {script}")
        _require_text(script, resolved_root / "tools" / "coad-validator" / "README.md", validator_readme, issues, f"validator README does not mention tool: {script}")
        _require_text(script, resolved_root / "docs" / "validator.md", validator_docs, issues, f"validator docs do not mention tool: {script}")
        _require_text(script, resolved_root / ".github" / "workflows" / "ci.yml", workflow, issues, f"CI does not run tool: {script}")
        for schema_name in REPORT_SCHEMAS.get(script, []):
            schema_path = resolved_root / "schema" / "reports" / schema_name
            if not schema_path.is_file():
                issues.append(DriftIssue(schema_path, f"missing report schema for {script}: {schema_name}"))
            _require_text(schema_name, resolved_root / "docs" / "tool-output-schemas.md", tool_schema_docs, issues, f"tool output schema docs do not mention schema: {schema_name}")
            if (script, f"reports/{schema_name}") not in manifest_producers:
                issues.append(
                    DriftIssue(
                        resolved_root / "schema" / "report-manifest.json",
                        f"manifest missing producer mapping: {script} -> reports/{schema_name}",
                    )
                )

    _require_text("schema/report-manifest.json", resolved_root / "docs" / "tool-output-schemas.md", tool_schema_docs, issues, "tool output schema docs do not mention report manifest")
    for schema_path in sorted((resolved_root / "schema" / "reports").glob("*.schema.json")):
        relative = f"reports/{schema_path.name}"
        if relative not in manifest_schemas:
            issues.append(
                DriftIssue(
                    resolved_root / "schema" / "report-manifest.json",
                    f"report schema missing from manifest: {relative}",
                )
            )
    for report in manifest_reports:
        schema = report.get("schema")
        producer = report.get("producer")
        if isinstance(schema, str) and not (resolved_root / "schema" / schema).is_file():
            issues.append(DriftIssue(resolved_root / "schema" / "report-manifest.json", f"manifest references missing report schema: {schema}"))
        if isinstance(producer, str) and producer not in scripts:
            issues.append(DriftIssue(resolved_root / "schema" / "report-manifest.json", f"manifest references missing producer command: {producer}"))

    return versioned_report(
        {
            "ok": not issues,
            "status": "clean" if not issues else "drift",
            "issues": [issue.to_json(resolved_root) for issue in issues],
        }
    )


def _tool_scripts(root: Path, issues: list[DriftIssue]) -> list[str]:
    pyproject = root / "tools" / "coad-validator" / "pyproject.toml"
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(DriftIssue(pyproject, "missing validator pyproject"))
        return []
    scripts = data.get("project", {}).get("scripts", {})
    if not isinstance(scripts, dict):
        issues.append(DriftIssue(pyproject, "missing [project.scripts] table"))
        return []
    return sorted(script for script in scripts if isinstance(script, str) and script.startswith("coad-"))


def _report_manifest(root: Path, issues: list[DriftIssue]) -> list[dict[str, Any]]:
    manifest_path = root / "schema" / "report-manifest.json"
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(DriftIssue(manifest_path, "missing report manifest"))
        return []
    except json.JSONDecodeError as exc:
        issues.append(DriftIssue(manifest_path, f"invalid report manifest JSON: {exc.msg}"))
        return []

    if payload.get("schema_version") != 1:
        issues.append(DriftIssue(manifest_path, "report manifest schema_version must be 1"))
    reports = payload.get("reports")
    if not isinstance(reports, list):
        issues.append(DriftIssue(manifest_path, "report manifest must contain reports list"))
        return []

    valid_reports: list[dict[str, Any]] = []
    for report in reports:
        if not isinstance(report, dict):
            issues.append(DriftIssue(manifest_path, "report manifest contains non-object report entry"))
            continue
        valid_reports.append(report)
    return valid_reports


def _read_text(path: Path, issues: list[DriftIssue]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(DriftIssue(path, "missing required drift check file"))
        return ""


def _require_text(
    needle: str,
    path: Path,
    haystack: str,
    issues: list[DriftIssue],
    message: str,
) -> None:
    if needle not in haystack:
        issues.append(DriftIssue(path, message))


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
