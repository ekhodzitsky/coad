from __future__ import annotations

import argparse
import json
from pathlib import Path

from .graph_report import build_graph_report
from .report import versioned_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a COAD contract graph")
    parser.add_argument("path", nargs="?", default=".", help="Path containing COAD contract Markdown files")
    parser.add_argument("--schema-dir", help="Directory containing COAD JSON schemas")
    parser.add_argument("--format", choices=["json"], default="json", help="Output format")
    args = parser.parse_args()

    root = Path(args.path)
    schema_dir = Path(args.schema_dir) if args.schema_dir else None

    try:
        payload = build_graph_report(root, schema_dir=schema_dir)
    except FileNotFoundError as exc:
        payload = versioned_report(
            {
                "ok": False,
                "status": "invalid",
                "contracts": 0,
                "issues": [
                    {
                        "severity": "error",
                        "path": str(root),
                        "message": str(exc),
                    }
                ],
            }
        )

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
