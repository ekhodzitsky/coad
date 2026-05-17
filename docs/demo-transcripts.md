# Demo Transcripts

These transcripts are meant to be run from the COAD repository root. They show
the two trust gates in the public README:

- adoption gate: a repository has no COAD entrypoint;
- quality gate: COAD files exist, but the module contract is not useful enough
  for agent-safe editing.

## Adoption Gate

The unstructured `before` repository has billing and checkout code, but no
`AGENTS.md` and no module contract.

```bash
$ uv run --project tools/coad-validator coad check examples/before-after/before --schema-dir schema
coad check: fail
```

The `after` repository adds `AGENTS.md`, a billing `MODULE_CONTRACT.md`, and
local billing `README.md`/`TODO.md`.

```bash
$ uv run --project tools/coad-validator coad check examples/before-after/after --schema-dir schema
coad check: pass
```

## Quality Gate

The `missing-consumer` fixture has COAD guidance and module context files, but
its public `BillingTotals` surface does not declare any consumer.

```bash
$ uv run --project tools/coad-validator coad check tools/coad-validator/tests/fixtures/invalid/missing-consumer --schema-dir schema --format json
{
  "checks": [
    {
      "name": "agent-guidance",
      "ok": true,
      "producer": "coad check",
      "required": true,
      "status": "pass"
    },
    {
      "name": "validation-report",
      "ok": false,
      "producer": "coad check",
      "required": true,
      "status": ""
    }
  ],
  "issues": [
    {
      "code": "semantic.public_surface_without_consumer",
      "message": "validation-report: public surface has no declared consumer: BillingTotals",
      "path": "MODULE_CONTRACT.md",
      "severity": "error"
    }
  ],
  "ok": false,
  "schema_version": 1,
  "status": "fail"
}
```

That failure is the point: `coad check .` rejects paperwork that does not name
the real public consumer.
