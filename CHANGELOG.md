# Changelog

## 0.9.0 - 2026-05-20

### Changed

- COAD became a methodology, not a tool. The Python validator
  (`tools/coad-validator/`, ~7600 LOC + 200 tests), every JSON schema
  (`schema/`), every example (`examples/`), every starter template
  (`templates/`), self-dogfooding contracts (`project-contracts/`),
  CI workflow (`.github/workflows/ci.yml`), and the rule-based
  `STANDARD.md` were removed from the active surface. The validator
  source moved to `docs/archive/coad-validator.v0.8.0/` for git history;
  schemas were deleted outright.
- `PRINCIPLES.md` returned to the repository root as the methodology's
  canonical statement.
- README, AGENTS.md, and AGENT_ONBOARDING.md were rewritten around a
  single message: COAD is prose. Adoption means writing four files and
  using judgment, not running a checker.
- No more `coad check .` integration point. Adopters that want
  automation build their own.

## 0.8.0 - 2026-05-20

### Changed

- Collapsed COAD into a fifteen-rule standard. `STANDARD.md` is now the
  source of truth for what `coad check .` enforces. Pre-v2 prose
  (`SPEC.md`, `PRINCIPLES.md`, `AGENT_FLOW.md`, `COAD_PROJECT_STANDARD.md`,
  `ADOPTION.md`, `GETTING_STARTED.md`, `GLOSSARY.md`, plus most files
  under `docs/`) moved to `docs/archive/` as historical context.
- `schema/module-contract.schema.json` shrank to five required fields:
  `schema_version`, `kind`, `module`, `purpose`, and `workcell`. Everything
  else is now optional. `surface.minItems`, `dependencies.required`, and
  `verification.required` were dropped from the schema.
- `coad check .` now distinguishes severity levels. Six rules were
  downgraded from `error` to `warning`/`info`:
  `semantic.surface_missing`,
  `semantic.public_surface_without_consumer`, `semantic.placeholder`,
  `semantic.proof_placeholder`, `semantic.context_file_empty`, and
  `workcell.budget_exceeded` (warning); `semantic.purpose_too_generic`
  (info). A run with only warnings exits zero.
- Evidence-layer schemas (`goal-contract`, `task-contract`,
  `proof-contract`, `handoff-contract`, `review-contract`,
  `integration-contract`, `proof-artifact`, `execution-ledger`,
  `conformance-profile`) moved to `schema/extensions/`. The validator
  resolves them with a `schema/` → `schema/extensions/` fallback so the
  default `coad check .` still works.
- `coad_validator.extensions.evidence` namespace re-exports the
  evidence-layer report builders for callers that want to opt in
  explicitly. The underlying implementation modules did not move.
- `examples/minimal/` collapsed to the Core shape (AGENTS.md +
  MODULE_CONTRACT.md + checkout/README.md + checkout/TODO.md). The
  evidence-heavy variant moved to `docs/archive/` (see the
  pre-v2 minimal example referenced from `docs/archive/README.md`).

## 0.7.7 - 2026-05-19

### Changed

- Reframed public docs around COAD Core for minimal adoption and COAD Evidence
  for optional agent/CI audit trails, keeping JSON details out of the normal
  human onboarding path.
- Renamed visible validator and CI wording from compliance language to boundary
  and evidence checks.

## 0.7.6 - 2026-05-19

### Added

- `coad check --format json` repair actions now include typed `action`,
  `action_code`, `target_field`, `expected_kind`, and `rerun` fields so agents
  can branch on stable repair protocol keys instead of parsing `minimal_fix`.

## 0.7.5 - 2026-05-19

### Added

- Public `coad check --format json` output now includes `agent_status`,
  `blocking_checks`, and machine-readable `next_actions` so agents can repair
  evidence trail failures without parsing prose.

## 0.7.4 - 2026-05-19

### Added

- `methodology-loop` reports now declare `claim: methodology_evidence`, list
  explicit limitations, and include per-phase source reports, blocking issues,
  and recommended repairs.

### Changed

- README and validator docs now describe COAD as checking the workflow evidence
  trail, not agent intent or semantic correctness by itself.

## 0.7.3 - 2026-05-19

### Added

- `coad check .` now emits a required `methodology-loop` report that aggregates
  orientation, scope, execution, proof, knowledge-update, and handoff evidence
  into phase statuses (`pass`, `weak`, `missing`, `unknown`, `skipped`).
- The minimal execution example now includes full proof output transcripts
  bound from JSON proof artifacts with `output_sha256` and `output_bytes`.

## 0.7.2 - 2026-05-19

### Added

- `coad check .` now binds JSON proof artifact `output_path` attachments with
  `output_sha256` and `output_bytes`, validates non-empty output, and reports
  computed expected values for missing output metadata.

## 0.7.1 - 2026-05-19

### Added

- `coad check .` now validates JSON proof artifact provenance: status must
  match `exit_code`, artifact timestamps must be ordered and fit within the
  ledger entry window, and `tool`, `cwd`, and `output_path` must be safe
  repository-relative values.

## 0.7.0 - 2026-05-18

### Added

- Added `proof-artifact.schema.json` for machine-readable proof artifacts.
- `coad check .` now validates `.json` proof artifacts against that schema and
  requires their `command` and `status` to match the linked ledger proof result.

## 0.6.9 - 2026-05-18

### Added

- Proof artifact metadata failures now include the computed expected
  `artifact_sha256` or `artifact_bytes` when the artifact exists, so agents can
  repair `EXECUTION_LEDGER.json` without running a separate digest command.

## 0.6.8 - 2026-05-18

### Added

- `coad check .` now binds passing ledger proof artifacts to their declared
  SHA-256 digest and byte size, so a ledger cannot pass by pointing at a
  swapped or stale proof file.

## 0.6.7 - 2026-05-18

### Added

- `coad check .` now verifies ledger-handoff integrity: completed
  `EXECUTION_LEDGER.json` entries must point at existing handoffs, match
  `HANDOFF.task_id` and `changed_files`, and require `HANDOFF.status: complete`.

## 0.6.6 - 2026-05-18

### Added

- `coad check .` now verifies proof artifact integrity for
  `EXECUTION_LEDGER.json`: passing proof results must declare a non-empty
  artifact that resolves from the ledger directory inside the checked root,
  while declared artifacts on non-passing results are still path-checked.

## 0.6.5 - 2026-05-18

### Added

- `coad check .` now verifies contract update integrity for changed
  methodology files, requiring `HANDOFF.contract_updates` entries with
  non-empty reasons while reporting stale entries as warnings.

## 0.6.4 - 2026-05-18

### Added

- `coad check .` now verifies proof result integrity across root `HANDOFF.md`,
  the referenced `TASK_CONTRACT.proof.required`, and `EXECUTION_LEDGER.json`.

## 0.6.3 - 2026-05-18

### Added

- `coad check .` now checks Git diff files against the task referenced by root
  `HANDOFF.md`, failing when changed files escape `TASK_CONTRACT.write_scope`
  or match path-like `forbidden_mutations`.
- `coad check .` now includes a context-aware handoff integrity check that
  compares root `HANDOFF.md` `changed_files` with the Git diff when that context
  is available.
- Added report builder, CLI, required-source, and negative-path JSON Schema
  compatibility coverage for manifest-backed report payloads.

### Fixed

- Registered the required `agent-guidance` report in the report manifest and
  added its JSON Schema so exported artifacts are schema-covered end to end.

## 0.6.2 - 2026-05-18

### Changed

- Agent onboarding docs, starter templates, and `examples/onboarding` now use
  the same first-adoption shape: a root `MODULE_CONTRACT.md` points to a real
  workcell with `workcell.context_path`, while that workcell owns its
  `README.md` and `TODO.md`.

### Fixed

- Validator static analysis now passes with explicit type narrowing for release
  gate metadata, lease manifest reads, and optional graph-index lookups.
- `coad check` now rejects duplicate module contract identifiers, missing
  workcell metadata, non-leaf ownership of descendant implementation paths, and
  project workcell write leases.

## 0.6.1 - 2026-05-18

### Added

- Reproducible before/after adoption demo showing `coad check` fail before
  COAD onboarding and pass after adding a billing workcell contract.
- Demo transcripts documenting both the adoption gate and the semantic quality
  gate for public surfaces without declared consumers.
- Regression fixture for `semantic.public_surface_without_consumer` so contract
  quality checks stay visible in public examples and tests.

### Fixed

- `coad check` now reports invalid UTF-8 in project-controlled inputs as
  structured validation issues instead of terminating with a traceback.
- Module context paths and lease write scopes now reject absolute paths,
  `..` traversal, and symlink escapes outside the repository.
- Attestation and export report builders now reuse cached validation evidence
  instead of re-scanning contracts for each report source.

## 0.6.0 - 2026-05-16

### Added

- Semantic module contract quality checks inside `coad check .` for obvious
  placeholders, too-generic purposes, public surfaces without consumers,
  placeholder proof commands, empty local context files, and missing
  `owns_paths`.
- Adoption smoke test notes for one-link onboarding against `phonex`.

## 0.5.1 - 2026-05-16

### Added

- `examples/parallel-work` showing an active `.coad/leases.yml` manifest with
  one composite orchestrator and two independent leaf write agents.

### Fixed

- Nested module contracts with `workcell.context_path: .` now resolve local
  context and ownership paths instead of accidentally using repository-root
  files when the repository is checked from above the example.

## 0.5.0 - 2026-05-16

### Added

- Optional `.coad/leases.yml` write lease validation.
- Lease manifest JSON Schema for active agent ownership declarations.
- Stable lease issue codes for unknown workcells, composite write leases,
  scope violations, and write conflicts.

## 0.4.0 - 2026-05-16

### Added

- Leaf `owns_paths` overlap detection for workcell ownership conflicts.
- Stable issue `code` values in validation and `coad check --format json`
  output.

## 0.3.0 - 2026-05-16

### Added

- Workcell tree validation for parent existence, child backlinks, parent
  cycles, leaf child declarations, and composite ownership of child paths.
- Root `project` workcell contract for COAD's own repository tree.

## 0.2.0 - 2026-05-16

### Added

- Logical workcell support through `workcell.context_path`.
- COAD self-contract hierarchy for docs, examples, schemas, templates, and validator internals.

### Changed

- COAD project contracts now pass context budgets without `budget_exceptions`.

## 0.1.0 - 2026-05-16

### Added

- Initial public COAD methodology for agent-navigable codebases.
- `coad check .` validator for module contracts, agent context files, contract graph integrity, and structured methodology reports.
- Public one-link agent onboarding through `https://github.com/ekhodzitsky/coad`.
