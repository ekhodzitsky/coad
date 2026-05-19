from __future__ import annotations

import argparse
import json
from pathlib import Path

from .check import build_check_report
from .report import versioned_report


def main() -> int:
    parser = argparse.ArgumentParser(prog="coad", description="COAD agent boundary and evidence toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Check COAD boundaries and evidence")
    check_parser.add_argument("path", nargs="?", default=".", help="Path containing COAD contracts")
    check_parser.add_argument("--schema-dir", help="Directory containing COAD JSON schemas")
    check_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()
    if args.command == "check":
        return _check(args)
    parser.error(f"unknown command: {args.command}")


def _check(args: argparse.Namespace) -> int:
    root = Path(args.path)
    schema_dir = Path(args.schema_dir) if args.schema_dir else None
    try:
        payload = build_check_report(root, schema_dir=schema_dir)
    except FileNotFoundError as exc:
        payload = versioned_report(
            {
                "ok": False,
                "status": "fail",
                "checks": [],
                "issues": [
                    {
                        "code": "schema.dir_not_found",
                        "severity": "error",
                        "path": str(root),
                        "message": str(exc),
                    }
                ],
            }
        )

    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"coad check: {payload['status']}")
        if payload["ok"]:
            _print_text_warnings(payload)
    return 0 if payload["ok"] else 1


def _print_text_warnings(payload: dict[str, object]) -> None:
    actions = payload.get("next_actions")
    if not isinstance(actions, list):
        return
    warnings = [
        action
        for action in actions
        if isinstance(action, dict)
        and action.get("severity") in {"warning", "info"}
        and action.get("blocks_completion") is False
    ]
    if not warnings:
        return
    print(f"  {len(warnings)} non-blocking issue(s):")
    for action in warnings:
        severity = action.get("severity", "warning")
        path = action.get("target_path", ".")
        minimal_fix = action.get("minimal_fix", action.get("action_code", ""))
        print(f"  - [{severity}] {path}: {minimal_fix}")


if __name__ == "__main__":
    raise SystemExit(main())
