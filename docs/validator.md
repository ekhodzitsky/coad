# Validator

COAD includes a Python reference validator under `tools/coad-validator`.

The validator is intentionally small. It exists to make the contract standard
executable before heavier orchestration tooling exists.

## What It Checks

- Markdown files with YAML frontmatter and `kind: *_contract`.
- JSON Schema conformance for each contract type.
- Module contracts point to real module directories with `README.md` and
  `TODO.md` agent context files.
- Workcell tree integrity: parents exist, declared children exist and point
  back to the parent, parent cycles are rejected, leaf workcells cannot declare
  children, and composite workcells cannot directly own child implementation
  paths.
- Workcell context budgets declared in `workcell.context_budget`: file count,
  source lines, contract length, README length, TODO length, surface count, and
  invariant count.
- Release metadata when a repository opts into it through `VERSION`,
  `CHANGELOG.md`, or the COAD validator package: `VERSION`,
  `[project].version`, package `__version__`, and a changelog entry for the
  current version must agree.
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
uv run coad check ../../examples/minimal --schema-dir ../../schema
```

`coad check` is the public default for agents and development flows. It prints
one result line in text mode:

```text
coad check: pass
```

Use `--format json` when an orchestrator needs structured issues and check
statuses.

The validator bundles the COAD schemas. `--schema-dir` remains useful for this
repository's own tests and schema development, but integrated repositories can
normally run `coad check .` without it.

## 2-Minute Onboarding Check

A repository can start with only:

- `AGENTS.md` containing COAD guidance and `coad check .`;
- one `MODULE_CONTRACT.md`;
- that module's `README.md`;
- that module's `TODO.md`.

`coad check .` passes this shape without requiring goal, task, proof, handoff,
review, integration, or ledger contracts. When those execution contracts appear,
the command automatically expands to the deeper orchestration checks.

Workcell budget failures are blocking by default. If a workcell is temporarily
too large, document the exception in `workcell.budget_exceptions` with a clear
reason, then split or shrink the workcell later.

Release metadata is intentionally opt-in for adopting repositories. A simple
application can start without `VERSION` and `CHANGELOG.md`. A repository that
ships COAD tooling or already has release metadata must keep it consistent.

## JSON Output

Use JSON output for CI or orchestration tools:

```bash
uv run coad check ../.. --schema-dir ../../schema --format json
```

Successful output:

```json
{
  "checks": [
    {
      "name": "agent-guidance",
      "ok": true,
      "producer": "coad check",
      "required": true,
      "status": "pass"
    }
  ],
  "issues": [],
  "ok": true,
  "schema_version": 1,
  "status": "pass"
}
```

Failed output includes structured issues:

```json
{
  "checks": [],
  "issues": [
    {
      "severity": "error",
      "path": "AGENTS.md",
      "message": "agent-guidance: missing AGENTS.md with COAD onboarding guidance"
    }
  ],
  "ok": false,
  "schema_version": 1,
  "status": "fail"
}
```

## Tool Output Schemas

The JSON output from `coad check . --format json` includes
`schema_version: 1` and is covered by `schema/reports/check-report.schema.json`.
Internal report payload schemas also live in `schema/reports/` for this
repository's tests and implementation.

See `docs/tool-output-schemas.md` and `docs/report-versioning.md`.

## Test Suite

```bash
cd tools/coad-validator
uv run pytest
```

The test suite includes conformance fixtures for valid and intentionally invalid
contract graphs.

## CI Contract

The repository CI runs the same checks expected from a local orchestrator. The
machine-readable gate list lives in `schema/release-manifest.json`; the drift
report is an internal report builder that checks that the manifest and
`.github/workflows/ci.yml` stay aligned.

```bash
cd tools/coad-validator
uv run --locked pytest
uv run --locked coad check ../.. --schema-dir ../../schema
jq empty ../../schema/*.json ../../schema/reports/*.json
```

External GitHub Actions in `.github/workflows/ci.yml` are pinned by commit SHA.
Update those pins deliberately when refreshing the CI supply chain.

See `docs/release-gates.md` for the release gate manifest contract.
