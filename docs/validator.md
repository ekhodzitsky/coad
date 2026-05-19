# Validator

COAD includes a Python reference validator under `tools/coad-validator`.

The validator is intentionally small. It exists to make the contract standard
executable before heavier orchestration tooling exists.

## What It Checks

- Markdown files with YAML frontmatter and `kind: *_contract`.
- JSON Schema conformance for each contract type.
- Module contracts point to real module directories with `README.md` and
  `TODO.md` agent context files. Context paths must stay inside the repository
  after symlink resolution.
- Module contract semantic quality: missing workcell metadata, obvious
  placeholders, too-generic module purpose, public surfaces without declared
  consumers, placeholder proof targets or commands, empty local context files,
  and missing `owns_paths`.
- Workcell tree integrity: parents exist, declared children exist and point
  back to the parent, parent cycles are rejected, leaf workcells cannot declare
  children, module identifiers are unique, and non-leaf workcells cannot
  directly own descendant implementation paths.
- Leaf workcell ownership: `owns_paths` cannot overlap between leaf workcells.
- Optional active lease manifest at `.coad/leases.yml`: write leases must point
  to known leaf workcells, must be unique per workcell, and must stay inside
  declared ownership. Explicit lease scopes must be repository-relative and
  cannot escape through `..` or symlinks.
- Workcell context budgets declared in `workcell.context_budget`: file count,
  source lines, contract length, README length, TODO length, surface count, and
  invariant count.
- Release metadata when a repository opts into it through `VERSION`,
  `CHANGELOG.md`, or the COAD validator package: `VERSION`,
  `[project].version`, package `__version__`, and a changelog entry for the
  current version must agree.
- Handoff integrity when context is available: if the checked root contains a
  `HANDOFF.md` and Git can determine a diff base, `coad check .` compares the
  real changed files with `handoff.changed_files`. Missing Git context,
  missing handoff, or an empty diff is reported as a skipped check rather than
  a failure.
- Task scope integrity when the same Git and handoff context is available:
  `coad check .` loads the referenced `TASK_CONTRACT.md`, then rejects changed
  files outside `write_scope` or inside path-like `forbidden_mutations`.
- Ledger handoff integrity when execution ledgers are available:
  `EXECUTION_LEDGER.json` entries must declare a relative `handoff_path` that
  exists inside the checked root. The referenced handoff must match the ledger
  `task_id` and `changed_files`; completed ledger entries require
  `HANDOFF.status: complete`.
- Proof result integrity when root handoff context is available: required proof
  commands from `TASK_CONTRACT.proof.required` must appear with `status: pass`
  in both `HANDOFF.md` and `EXECUTION_LEDGER.json`.
- Contract update integrity when Git and root handoff context are available:
  changed contracts, schemas, and methodology docs must appear in
  `HANDOFF.contract_updates` with a non-empty `reason`; stale entries are
  reported as warnings.
- Proof artifact integrity when execution ledgers are available: passing
  `EXECUTION_LEDGER.json` proof results must declare relative artifacts plus
  `artifact_sha256` and `artifact_bytes`. Declared artifacts must exist, resolve
  from the ledger directory inside the checked root, be non-empty, and match
  their declared digest and size. Missing artifacts for non-passing proof
  results are ignored, but declared paths are still validated. Missing digest
  metadata issues include the computed value when the artifact can be read.
  Artifacts ending in `.json` must also match `proof-artifact.schema.json`, and
  their `command` and `status` must match the ledger proof result. JSON proof
  artifacts also validate basic provenance: status/exit-code consistency,
  timestamp order and ledger-window bounds, safe relative `tool`, `cwd`, and
  `output_path`, plus existence of declared `output_path`. When `output_path`
  is present, the linked output must be non-empty and match declared
  `output_sha256` and `output_bytes`; missing output metadata issues include
  the computed value when the output can be read.
- Cross-contract graph references:
  - goal to modules, tasks, proofs, reviews, and integration;
  - task to modules and proof contracts;
  - review to target task;
  - handoff to target task;
  - integration to task contracts.

The validator skips `templates/` because templates contain placeholders. It also
skips `tests/fixtures/` and `examples/invalid/` during repository-wide
validation so intentional failures do not fail CI. Those paths are still checked
normally when passed directly to `coad check`. Invalid UTF-8 in
project-controlled Markdown, metadata, lease, ledger, profile, or drift-check
inputs is reported as a structured issue instead of a process traceback.

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
review, integration, ledger, or Git-diff context. When those execution
contracts appear, the command automatically expands to the deeper orchestration
checks.

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
      "code": "agent-guidance.failed",
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

Issue `code` values are stable machine keys. Agents should branch on `code`
instead of parsing English messages.

Lease-related failures use codes such as `lease.workcell_unknown`,
`lease.project_write_forbidden`, `lease.composite_write_forbidden`,
`lease.scope_invalid`, `lease.scope_outside_repository`,
`lease.scope_outside_ownership`, and `lease.write_conflict`.

Semantic quality failures use codes such as `semantic.placeholder`,
`semantic.purpose_too_generic`, `semantic.proof_placeholder`,
`semantic.surface_missing`, `semantic.public_surface_without_consumer`,
`semantic.context_file_empty`, `semantic.workcell_missing`,
`semantic.workcell_type_missing`, and `semantic.owns_path_missing`. These
checks are intentionally conservative: they catch contracts that are
structurally valid but not useful enough for a fresh agent to edit safely.

The example
`examples/invalid/missing-consumer` demonstrates the
quality gate: it has COAD guidance and module context files, but fails because
the public `BillingTotals` surface has no declared consumer.

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
