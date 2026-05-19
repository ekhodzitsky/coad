from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jsonschema import Draft202012Validator

from .report import versioned_report
from .schema import resolve_schema_path
from .text_io import read_utf8
from .validate import find_schema_dir

if TYPE_CHECKING:
    from .validate import ValidationReport


@dataclass(frozen=True)
class ProofArtifact:
    ledger_path: str
    event_id: str
    task_id: str
    command: str
    status: str
    artifact: str
    artifact_sha256: str
    artifact_bytes: int
    ok: bool


@dataclass(frozen=True)
class ArtifactValidation:
    ok: bool
    actual_sha256: str = ""
    actual_bytes: int | None = None


def build_proof_artifact_integrity_report(
    root: Path,
    schema_dir: Path | None = None,
    _contract_report: ValidationReport | None = None,
) -> dict[str, Any]:
    resolved_root = root.resolve()
    resolved_schema_dir = (schema_dir or find_schema_dir(resolved_root)).resolve()
    ledger_paths = _ledger_paths(resolved_root)
    if not ledger_paths:
        return _skipped("missing_ledger", "EXECUTION_LEDGER.json was not found")

    artifacts: list[ProofArtifact] = []
    issues: list[dict[str, str]] = []
    for ledger_path in ledger_paths:
        payload = _ledger_payload(ledger_path, resolved_root, issues)
        if payload is None:
            continue
        _collect_ledger_artifacts(resolved_root, ledger_path, payload, resolved_schema_dir, artifacts, issues)

    has_errors = any(issue["severity"] == "error" for issue in issues)
    return versioned_report(
        {
            "ok": not has_errors,
            "status": "violation" if has_errors else "pass",
            "artifacts": [_artifact_payload(artifact) for artifact in artifacts],
            "issues": issues,
        }
    )


def _collect_ledger_artifacts(
    root: Path,
    ledger_path: Path,
    payload: dict[str, Any],
    schema_dir: Path,
    artifacts: list[ProofArtifact],
    issues: list[dict[str, str]],
) -> None:
    ledger_display = _relative_path(ledger_path, root)
    for entry in _list_value(payload.get("entries")):
        if not isinstance(entry, dict):
            continue
        event_id = _string_value(entry.get("event_id"))
        task_id = _string_value(entry.get("task_id"))
        ledger_started_at = _string_value(entry.get("started_at"))
        ledger_completed_at = _string_value(entry.get("completed_at"))
        for proof_result in _list_value(entry.get("proof_results")):
            if not isinstance(proof_result, dict):
                continue
            command = _string_value(proof_result.get("command"))
            status = _string_value(proof_result.get("status"), "unknown")
            artifact = _string_value(proof_result.get("artifact"))
            artifact_sha256 = _string_value(proof_result.get("artifact_sha256"))
            artifact_bytes = _int_value(proof_result.get("artifact_bytes"))
            if not artifact:
                if status == "pass":
                    issues.append(
                        _issue(
                            "proof_artifact.missing",
                            ledger_display,
                            f"passing proof result must declare an artifact: {command}",
                        )
                    )
                continue
            artifact_validation = _validate_artifact(
                root,
                ledger_path.parent,
                artifact,
                artifact_sha256,
                artifact_bytes,
                status == "pass" and not artifact_sha256,
                command,
                status,
                ledger_started_at,
                ledger_completed_at,
                schema_dir,
                issues,
            )
            if status == "pass" and not artifact_sha256:
                issues.append(
                    _issue(
                        "proof_artifact.digest_missing",
                        ledger_display,
                        (
                            f"passing proof result must declare artifact_sha256: {command}"
                            f"{_expected_suffix(artifact_validation.actual_sha256)}"
                        ),
                    )
                )
            if status == "pass" and artifact_bytes is None:
                issues.append(
                    _issue(
                        "proof_artifact.bytes_missing",
                        ledger_display,
                        (
                            f"passing proof result must declare artifact_bytes: {command}"
                            f"{_expected_suffix(artifact_validation.actual_bytes)}"
                        ),
                    )
                )
            artifacts.append(
                ProofArtifact(
                    ledger_path=ledger_display,
                    event_id=event_id,
                    task_id=task_id,
                    command=command,
                    status=status,
                    artifact=artifact,
                    artifact_sha256=artifact_sha256,
                    artifact_bytes=artifact_bytes if artifact_bytes is not None else 0,
                    ok=artifact_validation.ok,
                )
            )


def _validate_artifact(
    root: Path,
    base_dir: Path,
    artifact: str,
    artifact_sha256: str,
    artifact_bytes: int | None,
    needs_sha256_hint: bool,
    command: str,
    status: str,
    ledger_started_at: str,
    ledger_completed_at: str,
    schema_dir: Path,
    issues: list[dict[str, str]],
) -> ArtifactValidation:
    candidate = Path(artifact)
    if candidate.is_absolute() or ".." in candidate.parts:
        issues.append(
            _issue(
                "proof_artifact.path_escape",
                artifact,
                f"proof artifact path escapes COAD root: {artifact}",
            )
        )
        return ArtifactValidation(ok=False)

    artifact_path = base_dir / candidate
    try:
        artifact_path.resolve(strict=False).relative_to(root)
    except ValueError:
        issues.append(
            _issue(
                "proof_artifact.path_escape",
                artifact,
                f"proof artifact path escapes COAD root: {artifact}",
            )
        )
        return ArtifactValidation(ok=False)

    if not artifact_path.is_file():
        issues.append(
            _issue(
                "proof_artifact.missing",
                artifact,
                f"proof artifact does not exist: {artifact}",
            )
        )
        return ArtifactValidation(ok=False)

    actual_bytes = artifact_path.stat().st_size
    if actual_bytes == 0:
        issues.append(
            _issue(
                "proof_artifact.empty",
                artifact,
                f"proof artifact is empty: {artifact}",
            )
        )
        return ArtifactValidation(ok=False, actual_bytes=actual_bytes)

    ok = True
    if artifact_bytes is not None and artifact_bytes != actual_bytes:
        issues.append(
            _issue(
                "proof_artifact.bytes_mismatch",
                artifact,
                f"proof artifact size mismatch for {artifact}: expected {artifact_bytes}, got {actual_bytes}",
            )
        )
        ok = False
    actual_sha256 = ""
    if artifact_sha256 or needs_sha256_hint:
        actual_sha256 = _sha256(artifact_path)
    if artifact_sha256:
        if artifact_sha256 != actual_sha256:
            issues.append(
                _issue(
                    "proof_artifact.digest_mismatch",
                    artifact,
                    f"proof artifact sha256 mismatch for {artifact}: expected {artifact_sha256}, got {actual_sha256}",
                )
            )
            ok = False
    if artifact_path.suffix == ".json":
        ok = (
            _validate_structured_artifact(
                root,
                base_dir,
                artifact_path,
                artifact,
                command,
                status,
                ledger_started_at,
                ledger_completed_at,
                schema_dir,
                issues,
            )
            and ok
        )
    return ArtifactValidation(ok=ok, actual_sha256=actual_sha256, actual_bytes=actual_bytes)


def _validate_structured_artifact(
    root: Path,
    base_dir: Path,
    artifact_path: Path,
    artifact: str,
    command: str,
    status: str,
    ledger_started_at: str,
    ledger_completed_at: str,
    schema_dir: Path,
    issues: list[dict[str, str]],
) -> bool:
    text, read_error = read_utf8(artifact_path)
    if read_error is not None:
        issues.append(_issue("proof_artifact.payload_read_failed", artifact, f"proof artifact {read_error}"))
        return False
    try:
        payload = json.loads(text or "")
    except json.JSONDecodeError as exc:
        issues.append(_issue("proof_artifact.payload_invalid_json", artifact, f"invalid proof artifact JSON: {exc.msg}"))
        return False
    if not isinstance(payload, dict):
        issues.append(_issue("proof_artifact.payload_invalid", artifact, "proof artifact must be a JSON object"))
        return False

    ok = _validate_artifact_schema(payload, artifact, schema_dir, issues)
    artifact_command = _string_value(payload.get("command"))
    if artifact_command and artifact_command != command:
        issues.append(
            _issue(
                "proof_artifact.payload_command_mismatch",
                artifact,
                f"proof artifact command does not match ledger for {artifact}: expected {command}, got {artifact_command}",
            )
        )
        ok = False
    artifact_status = _string_value(payload.get("status"))
    if artifact_status and artifact_status != status:
        issues.append(
            _issue(
                "proof_artifact.payload_status_mismatch",
                artifact,
                f"proof artifact status does not match ledger for {artifact}: expected {status}, got {artifact_status}",
            )
        )
        ok = False
    ok = _validate_exit_code(payload, artifact, issues) and ok
    ok = _validate_times(payload, artifact, ledger_started_at, ledger_completed_at, issues) and ok
    ok = _validate_payload_path(root, base_dir, artifact, payload, "cwd", "proof_artifact.payload_cwd_invalid", issues) and ok
    ok = _validate_tool(payload, artifact, issues) and ok
    ok = _validate_output_path(root, base_dir, artifact, payload, issues) and ok
    return ok


def _validate_exit_code(payload: dict[str, Any], artifact: str, issues: list[dict[str, str]]) -> bool:
    status = _string_value(payload.get("status"))
    exit_code = _int_value(payload.get("exit_code"))
    if status == "pass" and exit_code != 0:
        issues.append(
            _issue(
                "proof_artifact.payload_exit_code_mismatch",
                artifact,
                f"proof artifact status pass requires exit_code 0 for {artifact}, got {exit_code}",
            )
        )
        return False
    if status == "fail" and exit_code == 0:
        issues.append(
            _issue(
                "proof_artifact.payload_exit_code_mismatch",
                artifact,
                f"proof artifact status fail requires non-zero exit_code for {artifact}, got 0",
            )
        )
        return False
    return True


def _validate_times(
    payload: dict[str, Any],
    artifact: str,
    ledger_started_at: str,
    ledger_completed_at: str,
    issues: list[dict[str, str]],
) -> bool:
    ok = True
    started_at = _timestamp(payload.get("started_at"), "started_at", artifact, issues)
    completed_at = _timestamp(payload.get("completed_at"), "completed_at", artifact, issues)
    ledger_started = _timestamp(ledger_started_at, "ledger.started_at", artifact, issues) if ledger_started_at else None
    ledger_completed = _timestamp(ledger_completed_at, "ledger.completed_at", artifact, issues) if ledger_completed_at else None

    if started_at is None or completed_at is None:
        return False
    if completed_at < started_at:
        issues.append(
            _issue(
                "proof_artifact.payload_time_order",
                artifact,
                f"proof artifact completed_at is before started_at for {artifact}",
            )
        )
        ok = False
    if ledger_started is not None and started_at < ledger_started:
        issues.append(
            _issue(
                "proof_artifact.payload_time_outside_ledger",
                artifact,
                f"proof artifact started_at is outside ledger entry window for {artifact}",
            )
        )
        ok = False
    if ledger_completed is not None and completed_at > ledger_completed:
        issues.append(
            _issue(
                "proof_artifact.payload_time_outside_ledger",
                artifact,
                f"proof artifact completed_at is outside ledger entry window for {artifact}",
            )
        )
        ok = False
    return ok


def _validate_tool(payload: dict[str, Any], artifact: str, issues: list[dict[str, str]]) -> bool:
    tool = _string_value(payload.get("tool"))
    if not tool:
        return True
    candidate = Path(tool)
    if candidate.is_absolute() or ".." in candidate.parts:
        issues.append(
            _issue(
                "proof_artifact.payload_tool_invalid",
                artifact,
                f"proof artifact tool is not a safe relative value: {tool}",
            )
        )
        return False
    return True


def _validate_output_path(
    root: Path,
    base_dir: Path,
    artifact: str,
    payload: dict[str, Any],
    issues: list[dict[str, str]],
) -> bool:
    output_path = _string_value(payload.get("output_path"))
    if not output_path:
        return True
    resolved = _safe_payload_path(root, base_dir, output_path)
    if resolved is None:
        issues.append(
            _issue(
                "proof_artifact.payload_output_path_invalid",
                output_path,
                f"proof artifact output_path escapes COAD root: {output_path}",
            )
        )
        return False
    if not resolved.is_file():
        issues.append(
            _issue(
                "proof_artifact.payload_output_path_missing",
                output_path,
                f"proof artifact output_path does not exist: {output_path}",
            )
        )
        return False

    actual_bytes = resolved.stat().st_size
    if actual_bytes == 0:
        issues.append(
            _issue(
                "proof_artifact.payload_output_empty",
                output_path,
                f"proof artifact output_path is empty: {output_path}",
            )
        )
        return False

    actual_sha256 = _sha256(resolved)
    ok = True
    output_sha256 = _string_value(payload.get("output_sha256"))
    output_bytes = _int_value(payload.get("output_bytes"))
    if not output_sha256:
        issues.append(
            _issue(
                "proof_artifact.payload_output_digest_missing",
                artifact,
                (
                    f"proof artifact output_path must declare output_sha256 for {output_path}"
                    f"{_expected_suffix(actual_sha256)}"
                ),
            )
        )
        ok = False
    if output_bytes is None:
        issues.append(
            _issue(
                "proof_artifact.payload_output_bytes_missing",
                artifact,
                (
                    f"proof artifact output_path must declare output_bytes for {output_path}"
                    f"{_expected_suffix(actual_bytes)}"
                ),
            )
        )
        ok = False
    if output_bytes is not None and output_bytes != actual_bytes:
        issues.append(
            _issue(
                "proof_artifact.payload_output_bytes_mismatch",
                output_path,
                f"proof artifact output_path size mismatch for {output_path}: expected {output_bytes}, got {actual_bytes}",
            )
        )
        ok = False
    if output_sha256:
        if output_sha256 != actual_sha256:
            issues.append(
                _issue(
                    "proof_artifact.payload_output_digest_mismatch",
                    output_path,
                    f"proof artifact output_path sha256 mismatch for {output_path}: expected {output_sha256}, got {actual_sha256}",
                )
            )
            ok = False
    return ok


def _validate_payload_path(
    root: Path,
    base_dir: Path,
    artifact: str,
    payload: dict[str, Any],
    field: str,
    code: str,
    issues: list[dict[str, str]],
) -> bool:
    value = _string_value(payload.get(field))
    if not value:
        return True
    if _safe_payload_path(root, base_dir, value) is None:
        issues.append(_issue(code, artifact, f"proof artifact {field} escapes COAD root: {value}"))
        return False
    return True


def _safe_payload_path(root: Path, base_dir: Path, value: str) -> Path | None:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (base_dir / candidate).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def _validate_artifact_schema(
    payload: dict[str, Any],
    artifact: str,
    schema_dir: Path,
    issues: list[dict[str, str]],
) -> bool:
    resolved_path = resolve_schema_path(schema_dir, "proof-artifact.schema.json")
    schema_path = resolved_path if resolved_path is not None else schema_dir / "proof-artifact.schema.json"
    text, read_error = read_utf8(schema_path)
    if read_error is not None:
        issues.append(_issue("proof_artifact.schema_read_failed", "proof-artifact.schema.json", f"proof artifact schema {read_error}"))
        return False
    try:
        schema = json.loads(text or "")
    except json.JSONDecodeError as exc:
        issues.append(_issue("proof_artifact.schema_invalid_json", "proof-artifact.schema.json", f"invalid proof artifact schema JSON: {exc.msg}"))
        return False

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    for error in errors:
        issues.append(
            _issue(
                "proof_artifact.payload_schema_invalid",
                artifact,
                f"proof artifact schema violation at {_json_path(error.path)}: {error.message}",
            )
        )
    return not errors


def _ledger_payload(path: Path, root: Path, issues: list[dict[str, str]]) -> dict[str, Any] | None:
    text, read_error = read_utf8(path)
    display = _relative_path(path, root)
    if read_error is not None:
        issues.append(_issue("proof_artifact.ledger_read_failed", display, f"execution ledger {read_error}"))
        return None
    try:
        payload = json.loads(text or "")
    except json.JSONDecodeError as exc:
        issues.append(_issue("proof_artifact.ledger_invalid_json", display, f"invalid execution ledger JSON: {exc.msg}"))
        return None
    if not isinstance(payload, dict):
        issues.append(_issue("proof_artifact.ledger_invalid", display, "execution ledger must be a JSON object"))
        return None
    return payload


def _ledger_paths(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.rglob("EXECUTION_LEDGER.json"))
        if not _should_skip(path)
    ]


def _should_skip(path: Path) -> bool:
    parts = path.parts
    if any(part in {".git", ".venv", "__pycache__", "templates"} for part in parts):
        return True
    return any(first == "tests" and second == "fixtures" for first, second in zip(parts, parts[1:]))


def _artifact_payload(artifact: ProofArtifact) -> dict[str, Any]:
    return {
        "ledger_path": artifact.ledger_path,
        "event_id": artifact.event_id,
        "task_id": artifact.task_id,
        "command": artifact.command,
        "status": artifact.status,
        "artifact": artifact.artifact,
        "artifact_sha256": artifact.artifact_sha256,
        "artifact_bytes": artifact.artifact_bytes,
        "ok": artifact.ok,
    }


def _list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_value(value: object, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback


def _int_value(value: object) -> int | None:
    return value if type(value) is int and value >= 0 else None


def _timestamp(value: object, field: str, artifact: str, issues: list[dict[str, str]]) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        issues.append(
            _issue(
                "proof_artifact.payload_timestamp_invalid",
                artifact,
                f"proof artifact {field} timestamp is invalid for {artifact}: {value}",
            )
        )
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _expected_suffix(value: str | int | None) -> str:
    return f" (expected {value})" if value not in ("", None) else ""


def _json_path(path: Any) -> str:
    parts = list(path)
    if not parts:
        return "."
    return "." + ".".join(str(part) for part in parts)


def _skipped(reason: str, message: str) -> dict[str, Any]:
    return versioned_report(
        {
            "ok": True,
            "status": "skipped",
            "artifacts": [],
            "skip_reason": reason,
            "issues": [_issue("proof_artifact.skipped", "EXECUTION_LEDGER.json", message, severity="info")],
        }
    )


def _issue(code: str, path: str, message: str, severity: str = "error") -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "path": path,
        "message": message,
    }


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
