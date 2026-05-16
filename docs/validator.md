# Validator

COAD includes a Python reference validator under `tools/coad-validator`.

The validator is intentionally small. It exists to make the contract standard
executable before heavier orchestration tooling exists.

## What It Checks

- Markdown files with YAML frontmatter and `kind: *_contract`.
- JSON Schema conformance for each contract type.
- Cross-contract graph references:
  - goal to modules, tasks, proofs, reviews, and integration;
  - task to modules and proof contracts;
  - review to target task;
  - handoff to target task;
  - integration to task contracts.

The validator skips `templates/` because templates contain placeholders. It also
skips `tests/fixtures/` during repository-wide validation so intentional invalid
fixtures do not fail CI.

## Local Usage

```bash
cd tools/coad-validator
uv run coad-validate ../../examples/minimal --schema-dir ../../schema
uv run coad-validate ../.. --schema-dir ../../schema
```

## JSON Output

Use JSON output for CI or orchestration tools:

```bash
uv run coad-validate ../.. --schema-dir ../../schema --format json
```

Successful output:

```json
{
  "contracts": 7,
  "issues": [],
  "ok": true
}
```

Failed output includes structured issues:

```json
{
  "contracts": 6,
  "issues": [
    {
      "severity": "error",
      "path": "GOAL_CONTRACT.md",
      "message": "missing proof contract: missing-proof-contract"
    }
  ],
  "ok": false
}
```

## Test Suite

```bash
cd tools/coad-validator
uv run pytest
```

The test suite includes conformance fixtures for valid and intentionally invalid
contract graphs.
