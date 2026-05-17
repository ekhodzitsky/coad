# before-after

Purpose: show the smallest visible difference between an unstructured agent
handoff and a COAD-adopted module boundary.

Run from the repository root:

```bash
uv run --project tools/coad-validator coad check examples/before-after/before --schema-dir schema
uv run --project tools/coad-validator coad check examples/before-after/after --schema-dir schema
```

Expected result:

```text
coad check: fail
coad check: pass
```

The `before/` repository has billing and checkout code, but no agent-readable
COAD entrypoint. The `after/` repository adds `AGENTS.md`, a billing
`MODULE_CONTRACT.md`, and local billing context that names checkout as a
consumer of `BillingTotals`.

For the deeper semantic-quality failure where COAD files exist but the public
surface omits its consumer, see
`tools/coad-validator/tests/fixtures/invalid/missing-consumer`.
