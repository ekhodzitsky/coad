from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .report import versioned_report
from .report_sources import ATTESTATION_SOURCES, ReportSource


SOURCES = ATTESTATION_SOURCES


def build_attestation_report(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    resolved_root = root.resolve()
    resolved_schema_dir = (schema_dir or resolved_root / "schema").resolve()
    issues: list[dict[str, str]] = []
    reports = [
        _attested_report(source, resolved_root, resolved_schema_dir, issues)
        for source in SOURCES
    ]
    bundle_digest = _sha256(
        {
            "reports": [
                {
                    "name": report["name"],
                    "digest": report["digest"],
                    "ok": report["ok"],
                    "required": report["required"],
                }
                for report in reports
            ]
        }
    )
    return versioned_report(
        {
            "ok": not issues,
            "status": "attested" if not issues else "attestation_failed",
            "bundle_digest": bundle_digest,
            "reports": reports,
            "issues": issues,
        }
    )


def _attested_report(
    source: ReportSource,
    root: Path,
    schema_dir: Path,
    issues: list[dict[str, str]],
) -> dict[str, Any]:
    payload = source.build(root, schema_dir)
    ok = payload.get("ok") is True
    if source.required and not ok:
        issues.append(
            {
                "severity": "error",
                "path": _issue_path(payload, root),
                "message": f"required attestation report failed: {source.name}",
            }
        )
    status = payload.get("status")
    return {
        "name": source.name,
        "producer": source.producer,
        "required": source.required,
        "ok": ok,
        "status": status if isinstance(status, str) else "",
        "digest": _sha256(payload),
    }


def _issue_path(payload: dict[str, Any], root: Path) -> str:
    issues = payload.get("issues")
    if isinstance(issues, list):
        for issue in issues:
            if not isinstance(issue, dict):
                continue
            path = issue.get("path")
            if isinstance(path, str) and path:
                return path
    return _relative_path(root, root)


def _sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
