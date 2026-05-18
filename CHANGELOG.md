# Changelog

## Unreleased

### Changed

- Agent onboarding docs, starter templates, and `examples/onboarding` now use
  the same first-adoption shape: a root `MODULE_CONTRACT.md` points to a real
  workcell with `workcell.context_path`, while that workcell owns its
  `README.md` and `TODO.md`.

### Fixed

- Validator static analysis now passes with explicit type narrowing for release
  gate metadata, lease manifest reads, and optional graph-index lookups.

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
