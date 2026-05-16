from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ContractDocument:
    path: Path
    data: dict[str, Any]

    @property
    def kind(self) -> str:
        value = self.data.get("kind")
        return value if isinstance(value, str) else ""

    @property
    def identifier(self) -> str:
        for key in (
            "goal_id",
            "task_id",
            "module",
            "proof_id",
            "review_id",
            "integration_id",
        ):
            value = self.data.get(key)
            if isinstance(value, str) and value:
                return value
        return self.path.stem


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    message: str
    severity: str = "error"

    def format(self, root: Path) -> str:
        display = self.relative_path(root)
        return f"{display}: {self.message}"

    def relative_path(self, root: Path) -> str:
        try:
            return str(self.path.relative_to(root))
        except ValueError:
            return str(self.path)

    def to_json(self, root: Path) -> dict[str, str]:
        return {
            "severity": self.severity,
            "path": self.relative_path(root),
            "message": self.message,
        }


class ValidationFailure(Exception):
    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        super().__init__(f"{len(issues)} validation issue(s)")
