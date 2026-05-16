# COAD Validator

Reference validator for COAD contract files.

## Usage

```bash
uv run coad-validate ../../examples/minimal --schema-dir ../../schema
uv run coad-validate ../.. --schema-dir ../../schema --format json
uv run coad-status ../.. --schema-dir ../../schema
uv run coad-pack checkout-negative-total-guard ../../examples/minimal --schema-dir ../../schema
```

The validator checks Markdown YAML frontmatter against JSON schemas and verifies
that contract graph references point to existing contracts. `coad-status` adds a
conservative readiness report for orchestrators: valid-but-incomplete graphs are
reported as `ok: true` and `ready: false` with explicit blockers.

## Tests

```bash
uv run pytest
```
