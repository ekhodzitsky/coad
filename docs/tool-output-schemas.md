# Tool Output Schemas

COAD tools emit JSON for orchestration control planes. Those outputs are part of
the methodology contract, not incidental CLI formatting.

Report schemas live under `schema/reports/`:

- `validation-report.schema.json` covers `coad-validate --format json`.
- `status-report.schema.json` covers `coad-status`.
- `proof-matrix.schema.json` covers `coad-proof-matrix`.
- `graph-report.schema.json` covers `coad-graph`.
- `drift-report.schema.json` covers `coad-drift`.
- `context-pack.schema.json` covers successful `coad-pack` output.
- `pack-error.schema.json` covers failed `coad-pack` output.

The machine registry for these reports is `schema/report-manifest.json`.

## Contract

Tool JSON output should be stable enough for an orchestrator to consume without
screen scraping or natural-language parsing.

Every report payload MUST include `schema_version: 1`. Consumers should reject
unknown major versions unless they explicitly support them.

Changing a report schema should be treated as a compatibility event:

- update the schema and tests in the same change;
- document the reason in the commit message;
- keep existing fields stable unless the versioned contract explicitly changes;
- prefer adding fields over renaming or removing fields.

See `docs/report-versioning.md` for compatibility rules.

## Local Verification

```bash
cd tools/coad-validator
uv run --locked pytest tests/test_report_schemas.py tests/test_report_versioning.py
```

The tests execute the real CLIs, parse their JSON output, validate the payloads
against `schema/reports/*.json`, and check that the schemas themselves are valid
Draft 2020-12 JSON Schemas.
