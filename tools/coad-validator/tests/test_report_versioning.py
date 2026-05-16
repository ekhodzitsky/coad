from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"
FIXTURES = Path(__file__).parent / "fixtures"


def test_all_machine_reports_include_schema_version() -> None:
    commands = [
        [
            sys.executable,
            "-m",
            "coad_validator.cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--format",
            "json",
        ],
        [
            sys.executable,
            "-m",
            "coad_validator.status_cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ],
        [
            sys.executable,
            "-m",
            "coad_validator.proof_matrix_cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ],
        [
            sys.executable,
            "-m",
            "coad_validator.graph_report_cli",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ],
        [sys.executable, "-m", "coad_validator.drift_cli", str(ROOT)],
        [
            sys.executable,
            "-m",
            "coad_validator.pack_cli",
            "checkout-negative-total-guard",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ],
        [
            sys.executable,
            "-m",
            "coad_validator.pack_cli",
            "missing-task",
            str(FIXTURES / "valid" / "minimal-graph"),
            "--schema-dir",
            str(SCHEMA_DIR),
        ],
    ]

    for command in commands:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        payload = json.loads(result.stdout)
        assert payload["schema_version"] == 1
