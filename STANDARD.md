# COAD Standard

This document is the standard. Every rule below is checked by `coad check .`.
Anything else COAD says about agents, methodology, or orchestration is
guidance — not part of the standard.

The standard is intentionally small. It defines the file shape and contract
fields that make a repository *agent-navigable*: an agent can enter through
declared ownership boundaries, find local context, and edit safely.

`schema/module-contract.schema.json` and `schema/lease-manifest.schema.json`
are the source of truth for fields. This document points at them rather than
duplicating them.

## Severity levels

- **error** — `coad check .` exits non-zero. Repository does not conform.
- **warning** — `coad check .` exits zero but prints the issue. Repository
  conforms, but has a quality issue worth fixing.
- **info** — `coad check .` exits zero. Heuristic nudge, not an obligation.

## Core rules

### COAD-001 — AGENTS.md is the entry point

Statement: The repository root contains `AGENTS.md`. The file mentions
`coad check` and `MODULE_CONTRACT` (case-insensitive).
Schema: not schema-defined. Detected via file content.
Validator rule: `agent-guidance.failed`.
Severity: error.

### COAD-002 — At least one module contract exists

Statement: There is at least one Markdown file with YAML frontmatter
containing `kind: module_contract`.
Schema: `schema/module-contract.schema.json`, field `kind`.
Validator rule: `validation.module_contract_missing`.
Severity: error.

### COAD-003 — Module contracts validate against the schema

Statement: Every `kind: module_contract` document passes
`module-contract.schema.json`. The schema requires
`schema_version`, `kind`, `module`, `purpose`, and `workcell`. Everything
else is optional.
Schema: `schema/module-contract.schema.json`.
Validator rules: `schema.violation`, `schema.not_found`,
`schema.unknown_contract_kind`.
Severity: error.

### COAD-004 — Module contract declares a workcell with a type

Statement: The frontmatter contains a `workcell` object whose `type` is
`project`, `composite`, or `leaf`.
Schema: `module-contract.schema.json`, `workcell.type`.
Validator rules: `semantic.workcell_missing`, `semantic.workcell_type_missing`.
Severity: error.

### COAD-005 — Module contract declares at least one owns_path that exists

Statement: `workcell.owns_paths` lists at least one relative path inside the
repository. Each entry resolves to an existing file or directory.
Schema: `module-contract.schema.json`, `workcell.owns_paths`.
Validator rules: `semantic.owns_path_missing`,
`semantic.owns_path_invalid`, `semantic.owns_path_outside_repository`.
Severity: error.

### COAD-006 — Module context_path resolves to a real directory with README.md and TODO.md

Statement: `workcell.context_path` (or, when absent, the `module` field)
points to a real directory inside the repository. That directory contains
both `README.md` and `TODO.md`.
Schema: `module-contract.schema.json`, `workcell.context_path`.
Validator rules: `module.context_outside_repository` plus per-file context
checks.
Severity: error.

### COAD-007 — Module identifiers are unique repo-wide

Statement: No two `module_contract` documents declare the same `module:`.
Validator rule: `workcell.duplicate_module`.
Severity: error.

### COAD-008 — Workcell tree is consistent

Statement: For every declared `workcell.parent`, the parent contract exists.
For every declared `workcell.children` entry, the child contract exists and
its own `workcell.parent` points back to this module. Leaf workcells declare
no children. The parent chain contains no cycle. Non-leaf workcells do not
own implementation paths that belong to a descendant workcell.
Validator rules: `workcell.parent_missing`, `workcell.child_missing`,
`workcell.child_parent_mismatch`, `workcell.leaf_has_children`,
`workcell.parent_cycle`, `workcell.composite_owns_child_path`.
Severity: error.

### COAD-009 — Leaf owns_paths do not overlap

Statement: For any two leaf workcells, neither workcell's `owns_paths`
contains the other's.
Validator rule: `workcell.owns_path_overlap`.
Severity: error.

### COAD-010 — Lease manifest is consistent when present

Statement: If `.coad/leases.yml` exists, it validates against the lease
manifest schema. Every `workcell` reference resolves to a known leaf module
contract. `mode: write` is unique per workcell. The lease `scope` stays
inside that workcell's `owns_paths`. Lease paths are repository-relative.
Schema: `schema/lease-manifest.schema.json`.
Validator rule family: `lease.*` (`lease.workcell_unknown`,
`lease.project_write_forbidden`, `lease.composite_write_forbidden`,
`lease.scope_invalid`, `lease.scope_outside_repository`,
`lease.scope_outside_ownership`, `lease.write_conflict`,
`lease.schema_violation`).
Severity: error (active only when `.coad/leases.yml` exists).

## Quality rules

### COAD-011 — Module contract has at least one surface

Statement: The `surface:` field is a non-empty array.
Validator rule: `semantic.surface_missing`.
Severity: warning.

### COAD-012 — Public surfaces have at least one declared consumer

Statement: Every `surface` entry with `visibility: public` and a non-empty
`name` is referenced by at least one `consumers[].uses[]` entry.
Validator rule: `semantic.public_surface_without_consumer`.
Severity: warning.

### COAD-013 — Free-text contract fields are not placeholders

Statement: `purpose`, owners, surface names/signatures/contracts, dependency
reasons, consumer paths/uses, invariant rules, and surface/invariant proof
targets and commands do not match common placeholder patterns (`TODO`,
`TBD`, `<replace-me>`, `Your module`, etc.).
Validator rules: `semantic.placeholder`, `semantic.proof_placeholder`.
Severity: warning. (`semantic.purpose_too_generic` is info.)

### COAD-014 — Module README.md and TODO.md contain meaningful content

Statement: For every module contract, the README.md and TODO.md in the
resolved context directory contain at least one non-heading, non-placeholder
line.
Validator rule: `semantic.context_file_empty`.
Severity: warning.

### COAD-015 — Workcell context budgets are respected when declared

Statement: If `workcell.context_budget` declares any of `max_files`,
`max_source_lines`, `max_contract_lines`, `max_readme_lines`,
`max_todo_lines`, `max_surfaces`, or `max_invariants`, the actuals computed
by the validator do not exceed those caps unless covered by a
`workcell.budget_exceptions` entry with a non-empty `reason`.
Schema: `module-contract.schema.json`, `workcell.context_budget`.
Validator rule: `workcell.budget_exceeded`.
Severity: warning.

## What is *not* in the standard

These checks live in the validator and run automatically when they apply,
but they are not part of the standard. A repository that does not use them
is still COAD-conforming.

- **Evidence contracts** (`goal_contract`, `task_contract`, `proof_contract`,
  `handoff_contract`, `review_contract`, `integration_contract`,
  `EXECUTION_LEDGER.json`, proof artifacts). Their schemas live in
  `schema/extensions/`. The validator activates these checks only when the
  repository contains those documents. See `docs/archive/` for the v0.7.7
  prose if you want the orchestration story.
- **Methodology-loop evidence aggregation** (`methodology-loop` report,
  per-phase pass/weak/missing/skipped status). Activated by the presence of
  `HANDOFF.md` or `EXECUTION_LEDGER.json`.
- **Release metadata** (`VERSION`, `CHANGELOG.md`, validator package
  `__version__`). This is COAD's own release plumbing, not a rule for
  adopters.
- **Cross-contract graph references** between goal/task/proof/review
  /integration contracts. Activated by their presence.

If a repository does not need any of these, COAD-001 through COAD-015 are
sufficient.

## Validator output

`coad check .` prints one line in text mode:

```text
coad check: pass
```

or

```text
coad check: fail
```

Use `coad check . --format json` to see the full report. Warnings are
visible in JSON `issues[]` with `"severity": "warning"`; they do not change
`ok`.

## Versioning

The standard moves in lockstep with `VERSION`. A rule change that turns a
warning into an error, adds a new error-level rule, or removes a field from
the required list of `module-contract.schema.json` is a major version bump.
Renaming a `code` is also a major bump. Adding a new warning is a minor
bump.
