from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from coad_validator.status import build_status_report

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
FIXTURES = Path(__file__).parent / "fixtures"


def test_status_report_marks_pending_goal_not_ready() -> None:
    payload = build_status_report(FIXTURES / "valid" / "minimal-graph", schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["ready"] is False
    goal = payload["goals"][0]
    assert goal["status"] == "not_ready"
    assert goal["declared_status"] == "proposed"
    messages = [blocker["message"] for blocker in goal["blockers"]]
    assert "goal status is proposed" in messages
    assert "task checkout-negative-total-guard status is pending" in messages


def test_status_report_marks_complete_contract_graph_ready(tmp_path: Path) -> None:
    source = FIXTURES / "valid" / "minimal-graph"
    target = tmp_path / "ready-graph"
    shutil.copytree(source, target)
    _replace_text(target / "GOAL_CONTRACT.md", "status: proposed", "status: ready")
    _replace_text(target / "TASK_CONTRACT.md", "status: pending", "status: complete")

    payload = build_status_report(target, schema_dir=SCHEMA_DIR)

    assert payload["ok"] is True
    assert payload["ready"] is True
    goal = payload["goals"][0]
    assert goal["status"] == "ready"
    assert goal["blockers"] == []
    assert goal["tasks"][0]["status"] == "ready"


def test_status_cli_json_output_for_invalid_contracts() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.status_cli",
            str(FIXTURES / "invalid" / "missing-proof"),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["ready"] is False
    assert payload["status"] == "invalid"
    assert "missing proof contract: missing-proof-contract" in payload["issues"][0]["message"]


def test_status_cli_can_fail_on_not_ready_graph() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.status_cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--fail-on-not-ready",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["ready"] is False


def test_status_cli_fail_on_not_ready_accepts_ready_graph(tmp_path: Path) -> None:
    source = FIXTURES / "valid" / "minimal-graph"
    target = tmp_path / "ready-graph"
    shutil.copytree(source, target)
    _replace_text(target / "GOAL_CONTRACT.md", "status: proposed", "status: ready")
    _replace_text(target / "TASK_CONTRACT.md", "status: pending", "status: complete")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "coad_validator.status_cli",
            str(target),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--fail-on-not-ready",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["ready"] is True


def _replace_text(path: Path, old: str, new: str) -> None:
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
