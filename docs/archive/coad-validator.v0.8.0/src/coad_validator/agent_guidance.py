from __future__ import annotations

from pathlib import Path
from typing import Any

from .report import versioned_report
from .text_io import read_utf8


def build_agent_guidance_report(root: Path, _schema_dir: Path | None = None) -> dict[str, Any]:
    agents_path = root / "AGENTS.md"
    issues: list[dict[str, str]] = []
    if not agents_path.is_file():
        issues.append(_issue("missing AGENTS.md with COAD onboarding guidance"))
    else:
        text, read_error = read_utf8(agents_path)
        if read_error is not None:
            issues.append(_issue(f"AGENTS.md {read_error}"))
        else:
            normalized = text.lower() if text is not None else ""
            if "coad check" not in normalized:
                issues.append(_issue("AGENTS.md must tell agents to run `coad check .`"))
            if "module_contract" not in normalized and "module contract" not in normalized:
                issues.append(_issue("AGENTS.md must tell agents to add or maintain a MODULE_CONTRACT"))

    return versioned_report(
        {
            "ok": not issues,
            "status": "pass" if not issues else "guidance_issues",
            "issues": issues,
        }
    )


def _issue(message: str) -> dict[str, str]:
    return {
        "severity": "error",
        "path": "AGENTS.md",
        "message": message,
    }
