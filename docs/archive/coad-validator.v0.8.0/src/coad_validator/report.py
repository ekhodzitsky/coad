from __future__ import annotations

from typing import Any

REPORT_SCHEMA_VERSION = 1


def versioned_report(payload: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version": REPORT_SCHEMA_VERSION, **payload}
