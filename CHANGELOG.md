# Changelog

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
