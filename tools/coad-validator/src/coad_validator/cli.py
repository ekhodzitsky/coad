from __future__ import annotations

import argparse
import json
from pathlib import Path

from .validate import validate_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate COAD contract files")
    parser.add_argument("path", nargs="?", default=".", help="Path containing COAD contract Markdown files")
    parser.add_argument("--schema-dir", help="Directory containing COAD JSON schemas")
    parser.add_argument("--no-graph", action="store_true", help="Skip cross-contract graph checks")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    args = parser.parse_args()

    root = Path(args.path)
    schema_dir = Path(args.schema_dir) if args.schema_dir else None

    try:
        report = validate_path(root, schema_dir=schema_dir, check_graph=not args.no_graph)
    except FileNotFoundError as exc:
        if args.format == "json":
            print(
                json.dumps(
                    {
                        "ok": False,
                        "contracts": 0,
                        "issues": [
                            {
                                "severity": "error",
                                "path": str(root),
                                "message": str(exc),
                            }
                        ],
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2
        print(f"coad-validate: {exc}")
        return 2

    if args.format == "json":
        print(
            json.dumps(
                {
                    "ok": report.ok,
                    "contracts": len(report.documents),
                    "issues": [issue.to_json(report.root) for issue in report.issues],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0 if report.ok else 1

    if report.ok:
        print(f"coad-validate: ok ({len(report.documents)} contract file(s))")
        return 0

    print(f"coad-validate: failed ({len(report.issues)} issue(s))")
    for issue in report.issues:
        print(f"- {issue.format(report.root)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
