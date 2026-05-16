from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pack import PackFailure, build_context_pack
from .report import versioned_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a COAD context pack for one task")
    parser.add_argument("task_id", help="Task contract id to pack")
    parser.add_argument("path", nargs="?", default=".", help="Path containing COAD contract Markdown files")
    parser.add_argument("--schema-dir", help="Directory containing COAD JSON schemas")
    parser.add_argument("--format", choices=["json"], default="json", help="Output format")
    args = parser.parse_args()

    schema_dir = Path(args.schema_dir) if args.schema_dir else None
    try:
        payload = build_context_pack(Path(args.path), args.task_id, schema_dir=schema_dir)
    except PackFailure as exc:
        print(json.dumps(versioned_report({"ok": False, "error": str(exc)}), indent=2, sort_keys=True))
        return 1

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
