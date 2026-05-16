# Changelog

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
