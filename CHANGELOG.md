# Changelog

## Unreleased

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
