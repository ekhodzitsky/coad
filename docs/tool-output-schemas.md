# Tool Output Schemas

`coad check . --format json` emits JSON for orchestration control planes. That
output is part of the methodology contract, not incidental CLI formatting.

Report schemas live under `schema/reports/`:

- `check-report.schema.json` covers the public `coad check --format json`
  payload.
- The remaining report schemas cover internal report payloads used by
  `coad check`, tests, and repository self-checks: validation, status, proof
  matrix, graph, schedule, ledger, profile, policy, attestation, export, drift,
  context pack, and pack errors.

The machine registry for these reports is `schema/report-manifest.json`.

## Contract

Public JSON output should be stable enough for an orchestrator to consume
without screen scraping or natural-language parsing.

Every report payload MUST include `schema_version: 1`. Consumers should reject
unknown major versions unless they explicitly support them.

Structured issues SHOULD include a stable `code` field such as
`workcell.parent_missing`, `workcell.owns_path_overlap`,
`lease.write_conflict`, or `graph.proof_missing`. Agents should use `code` for
automated repair routing and treat `message` as human-facing context.

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

The tests execute the public command and internal report modules, parse their
JSON output, validate the payloads against `schema/reports/*.json`, and check
that the schemas themselves are valid Draft 2020-12 JSON Schemas.
