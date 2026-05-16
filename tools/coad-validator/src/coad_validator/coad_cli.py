from __future__ import annotations

import argparse
import json
from pathlib import Path

from .check import build_check_report
from .report import versioned_report


def main() -> int:
    parser = argparse.ArgumentParser(prog="coad", description="COAD methodology toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Check COAD methodology compliance")
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
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
