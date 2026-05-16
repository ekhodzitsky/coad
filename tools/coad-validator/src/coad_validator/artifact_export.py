from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .attest import build_attestation_report
from .report import versioned_report
from .report_sources import ATTESTATION_SOURCES, ReportSource


def export_artifacts(
    root: Path,
    schema_dir: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    resolved_root = root.resolve()
    resolved_schema_dir = (schema_dir or resolved_root / "schema").resolve()
    resolved_output_dir = (output_dir or resolved_root / ".coad-export").resolve()
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    issues: list[dict[str, str]] = []
    artifacts: list[dict[str, Any]] = []

    attestation = build_attestation_report(resolved_root, schema_dir=resolved_schema_dir)
    artifacts.append(
        _write_artifact(
            resolved_output_dir,
            "attestation-report",
            "coad-attest",
            "attestation.json",
            True,
            attestation,
        )
    )

    for source in ATTESTATION_SOURCES:
        payload = source.build(resolved_root, resolved_schema_dir)
        artifacts.append(
            _write_source_artifact(
                resolved_output_dir,
                source,
                payload,
                resolved_root,
                issues,
            )
        )

    bundle_digest = _sha256(
        {
            "artifacts": [
                {
                    "name": artifact["name"],
                    "path": artifact["path"],
                    "digest": artifact["digest"],
                    "bytes": artifact["bytes"],
                    "ok": artifact["ok"],
                    "required": artifact["required"],
                }
                for artifact in artifacts
            ]
        }
    )
    payload = versioned_report(
        {
            "ok": not issues,
            "status": "exported" if not issues else "export_failed",
            "bundle_digest": bundle_digest,
            "attestation_bundle_digest": attestation.get("bundle_digest", ""),
            "artifact_count": len(artifacts),
            "artifacts": artifacts,
            "issues": issues,
        }
    )
    _write_json(resolved_output_dir / "manifest.json", payload)
    return payload


def _write_source_artifact(
    output_dir: Path,
    source: ReportSource,
    payload: dict[str, Any],
    root: Path,
    issues: list[dict[str, str]],
) -> dict[str, Any]:
    ok = payload.get("ok") is True
    if source.required and not ok:
        issues.append(
            {
                "severity": "error",
                "path": _issue_path(payload, root),
                "message": f"required artifact report failed: {source.name}",
            }
        )
    return _write_artifact(
        output_dir,
        source.name,
        source.producer,
        f"{source.name}.json",
        source.required,
        payload,
    )


def _write_artifact(
    output_dir: Path,
    name: str,
    producer: str,
    relative_path: str,
    required: bool,
    payload: dict[str, Any],
) -> dict[str, Any]:
    artifact_path = output_dir / relative_path
    text = _write_json(artifact_path, payload)
    status = payload.get("status")
    return {
        "name": name,
        "producer": producer,
        "path": relative_path,
        "required": required,
        "ok": payload.get("ok") is True,
        "status": status if isinstance(status, str) else "",
        "digest": _sha256(payload),
        "bytes": len(text.encode("utf-8")),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> str:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    return text


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
