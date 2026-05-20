from __future__ import annotations

import argparse
import json
from pathlib import Path

from .artifact_export import export_artifacts
from .report import versioned_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a COAD evidence artifact bundle")
    parser.add_argument("path", nargs="?", default=".", help="Path containing COAD contracts and evidence")
    parser.add_argument("--schema-dir", help="Directory containing COAD JSON schemas")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where exported artifacts are written",
    )
    parser.add_argument("--format", choices=["json"], default="json", help="Output format")
    args = parser.parse_args()

    root = Path(args.path)
    schema_dir = Path(args.schema_dir) if args.schema_dir else None
    output_dir = Path(args.output_dir)

    try:
        payload = export_artifacts(root, schema_dir=schema_dir, output_dir=output_dir)
    except FileNotFoundError as exc:
        payload = versioned_report(
            {
                "ok": False,
                "status": "export_failed",
                "bundle_digest": "",
                "attestation_bundle_digest": "",
                "artifact_count": 0,
                "artifacts": [],
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
