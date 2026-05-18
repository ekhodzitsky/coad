from __future__ import annotations

import ast
import tomllib
from pathlib import Path

from .model import ValidationIssue


def validate_release_metadata(root: Path) -> list[ValidationIssue]:
    version_path = root / "VERSION"
    changelog_path = root / "CHANGELOG.md"
    pyproject_path = root / "tools" / "coad-validator" / "pyproject.toml"
    package_init_path = root / "tools" / "coad-validator" / "src" / "coad_validator" / "__init__.py"

    if not any(path.exists() for path in (version_path, changelog_path, pyproject_path, package_init_path)):
        return []

    issues: list[ValidationIssue] = []
    if not version_path.is_file():
        issues.append(ValidationIssue(version_path, "release metadata is missing VERSION"))
    if not changelog_path.is_file():
        issues.append(ValidationIssue(changelog_path, "release metadata is missing CHANGELOG.md"))

    version = _read_version(version_path)
    if version_path.exists() and version is None:
        issues.append(ValidationIssue(version_path, "VERSION must contain exactly one non-empty version line"))

    pyproject_version, pyproject_issue = _read_pyproject_version_report(pyproject_path)
    if pyproject_issue is not None:
        issues.append(pyproject_issue)
    elif pyproject_path.exists() and pyproject_version is None:
        issues.append(ValidationIssue(pyproject_path, "pyproject.toml is missing [project].version"))
    if version is not None and pyproject_version is not None and pyproject_version != version:
        issues.append(
            ValidationIssue(
                pyproject_path,
                f"pyproject version {pyproject_version} does not match VERSION {version}",
            )
        )

    package_version, package_issue = _read_package_version_report(package_init_path)
    if package_issue is not None:
        issues.append(package_issue)
    elif package_init_path.exists() and package_version is None:
        issues.append(ValidationIssue(package_init_path, "package __init__.py is missing __version__"))
    if version is not None and package_version is not None and package_version != version:
        issues.append(
            ValidationIssue(
                package_init_path,
                f"package __version__ {package_version} does not match VERSION {version}",
            )
        )

    if version is not None and changelog_path.exists() and not _changelog_has_version(changelog_path, version):
        issues.append(ValidationIssue(changelog_path, f"CHANGELOG.md is missing an entry for VERSION {version}"))

    return issues


def _read_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != 1:
        return None
    return lines[0]


def _read_pyproject_version_report(path: Path) -> tuple[str | None, ValidationIssue | None]:
    try:
        return _read_pyproject_version(path), None
    except tomllib.TOMLDecodeError as exc:
        return None, ValidationIssue(path, f"pyproject.toml is invalid TOML: {exc}")


def _read_pyproject_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    version = project.get("version")
    return version if isinstance(version, str) and version else None


def _read_package_version_report(path: Path) -> tuple[str | None, ValidationIssue | None]:
    try:
        return _read_package_version(path), None
    except SyntaxError as exc:
        return None, ValidationIssue(path, f"package __init__.py is invalid Python: {exc.msg}")


def _read_package_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "__version__" for target in statement.targets):
            continue
        value = statement.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value:
            return value.value
    return None


def _changelog_has_version(path: Path, version: str) -> bool:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("## ") and version in stripped:
            return True
    return False
