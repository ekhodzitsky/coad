# COAD Validator

Reference validator for COAD contract files.

## Usage

```bash
uv run coad-validate ../../examples/minimal --schema-dir ../../schema
uv run coad-validate ../.. --schema-dir ../../schema --format json
uv run coad-status ../.. --schema-dir ../../schema
uv run coad-status ../.. --schema-dir ../../schema --fail-on-not-ready
uv run coad-proof-matrix ../.. --schema-dir ../../schema
uv run coad-graph ../.. --schema-dir ../../schema
uv run coad-schedule ../.. --schema-dir ../../schema
uv run coad-ledger ../.. --schema-dir ../../schema
uv run coad-profile ../.. --schema-dir ../../schema
uv run coad-policy ../.. --schema-dir ../../schema
uv run coad-attest ../.. --schema-dir ../../schema
uv run coad-export ../.. --schema-dir ../../schema --output-dir /tmp/coad-export
uv run coad-drift ../..
uv run coad-pack checkout-negative-total-guard ../../examples/minimal --schema-dir ../../schema
```

The validator checks Markdown YAML frontmatter against JSON schemas and verifies
that contract graph references point to existing contracts. `coad-status` adds a
conservative readiness report for orchestrators: valid-but-incomplete graphs are
reported as `ok: true` and `ready: false` with explicit blockers.
`coad-schedule` turns task dependencies and write scopes into execution waves
that an orchestrator can dispatch without overlapping writes inside a wave.
`coad-ledger` audits durable execution ledgers so completed task events cannot
claim success without passing every required task proof command.
`coad-profile` reports the declared COAD conformance level and the concrete
tool evidence supporting it.
`coad-policy` enforces goal policy constraints such as external side-effect
permission and required contract update handoff fields.
`coad-attest` builds a hashable bundle that binds the required reports together
for acceptance and audit.
`coad-export` writes those reports plus the attestation into a deterministic
artifact directory with a machine-readable manifest.

JSON outputs are covered by report schemas in `../../schema/reports/`.

## Tests

```bash
uv run pytest
```
