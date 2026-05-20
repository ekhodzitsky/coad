from __future__ import annotations

import argparse
import json
from pathlib import Path

from .drift import build_drift_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Check COAD repository drift")
    parser.add_argument("path", nargs="?", default=".", help="COAD repository root")
    parser.add_argument("--format", choices=["json"], default="json", help="Output format")
    args = parser.parse_args()

    payload = build_drift_report(Path(args.path))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
