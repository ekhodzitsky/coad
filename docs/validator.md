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

## Readiness Status

Use `coad-status` when an orchestrator needs to know whether the validated
contract graph is ready or blocked:

```bash
cd tools/coad-validator
uv run coad-status ../.. --schema-dir ../../schema
```

The status report is intentionally conservative. A goal is `ready` only when:

- the goal contract declares `status: ready`;
- every referenced task contract declares `status: complete`;
- every task has a complete handoff;
- every required task proof command appears as a passing handoff proof result.

Valid but incomplete graphs return `ok: true` and `ready: false` with blockers.
Invalid graphs return `ok: false`, `ready: false`, and validation issues.

For hard readiness gates, add `--fail-on-not-ready`:

```bash
uv run coad-status ../.. --schema-dir ../../schema --fail-on-not-ready
```

This keeps status reporting and acceptance gating separate. A CI job can publish
readiness without failing, while an orchestrator can fail a handoff or release
gate on the same report.

## Test Suite

```bash
cd tools/coad-validator
uv run pytest
```

The test suite includes conformance fixtures for valid and intentionally invalid
contract graphs.

## CI Contract

The repository CI runs the same checks expected from a local orchestrator:

```bash
cd tools/coad-validator
uv run --locked pytest
uv run --locked coad-validate ../.. --schema-dir ../../schema
uv run --locked coad-validate ../.. --schema-dir ../../schema --format json
uv run --locked coad-status ../.. --schema-dir ../../schema
uv run --locked coad-pack checkout-negative-total-guard ../../examples/minimal --schema-dir ../../schema
jq empty ../../schema/*.json
```

External GitHub Actions in `.github/workflows/ci.yml` are pinned by commit SHA.
Update those pins deliberately when refreshing the CI supply chain.
