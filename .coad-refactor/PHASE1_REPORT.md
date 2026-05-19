# Phase 1 — Refactor Plan for Standard-First COAD

Branch: `v2-standard-only`
Scope: reconnaissance only. No code, schema, or file moves yet.
Current package version: `0.7.7`.

The codebase currently mixes three ambitions:

1. a **standard** (file shape + JSON schemas + a few rules);
2. a **methodology** (PRINCIPLES, AGENT_FLOW, COAD_PROJECT_STANDARD prose);
3. an **orchestration framework** (execution ledgers, proof artifacts,
   methodology-loop reports, repair protocols, ~50 Python modules, ~7.6 kLOC).

The goal of v2 is to keep the standard and drop or extension-isolate the rest.

The validator already has a partial split: `ONBOARDING_METHODOLOGY_SOURCES`
runs three Core sources (`agent-guidance`, `validation-report`,
`methodology-loop`) on adoption-only repositories, while
`CORE_METHODOLOGY_SOURCES` adds 12 Evidence sources as soon as a target
repository contains `task_contract`, `goal_contract`, `proof_contract`,
`handoff_contract`, `integration_contract`, or `review_contract` frontmatter.
We will lean on this seam.

---

## A. Validator Rule Inventory

All rule codes were extracted from `src/coad_validator/**/*.py`. They are
grouped here by family. Every code currently surfaces as `severity: error`
because `ValidationIssue.severity` defaults to `"error"` and no rule sets it
otherwise.

| rule_id (family.code)                             | What it checks                                                                                  | Current severity | Strictly part of standard? | Move to                  |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ---------------- | -------------------------- | ------------------------ |
| `validation.module_contract_missing`              | At least one `kind: module_contract` Markdown file exists                                       | error            | yes                        | core                     |
| `frontmatter.read_failed`                         | Markdown file with frontmatter could be read as UTF-8                                           | error            | yes (infra)                | core                     |
| `schema.unknown_contract_kind`                    | `kind:` matches a known contract kind                                                           | error            | yes                        | core (module only); orchestration (others) |
| `schema.not_found` / `schema.dir_not_found`       | The schema JSON file exists at the schema directory                                             | error            | yes                        | core                     |
| `schema.violation`                                | Contract validates against its JSON Schema                                                      | error            | yes                        | core                     |
| `module.context_outside_repository`               | `workcell.context_path` resolves inside the repo (no `..`, no symlink escape)                   | error            | yes                        | core                     |
| `semantic.workcell_missing`                       | Module contract declares a `workcell` object                                                    | error            | yes                        | core                     |
| `semantic.workcell_type_missing`                  | `workcell.type` is set                                                                          | error            | yes                        | core                     |
| `semantic.owns_path_missing` (cluster A)          | At least one `workcell.owns_paths` entry is declared                                            | error            | yes                        | core                     |
| `semantic.owns_path_missing` (cluster B)          | Each declared owns_path exists on disk                                                          | error            | yes                        | core                     |
| `semantic.owns_path_invalid`                      | Each declared owns_path is relative and contains no `..`                                        | error            | yes                        | core                     |
| `semantic.owns_path_outside_repository`           | Each declared owns_path resolves inside the repo                                                | error            | yes                        | core                     |
| `semantic.surface_missing`                        | Module contract declares at least one surface entry                                             | error            | maybe (downgrade)          | core, severity=warning   |
| `semantic.public_surface_without_consumer`        | A `visibility: public` surface has at least one consumer mention                                | error            | maybe (downgrade)          | core, severity=warning   |
| `semantic.placeholder`                            | Free-text fields contain no obvious `TODO`/`TBD`/`<...>` placeholders                           | error            | maybe (downgrade)          | core, severity=warning   |
| `semantic.purpose_too_generic`                    | `purpose` is not "module", "service", "tool", etc.                                              | error            | no (heuristic)             | core, severity=info      |
| `semantic.proof_placeholder`                      | Surface/invariant proof `target`/`command` is not a placeholder                                 | error            | no (heuristic)             | core, severity=warning   |
| `semantic.context_file_empty`                     | Module's README.md and TODO.md contain at least one non-heading non-placeholder line            | error            | maybe (downgrade)          | core, severity=warning   |
| `workcell.duplicate_module`                       | Module `module:` identifier is unique repo-wide                                                 | error            | yes                        | core                     |
| `workcell.parent_missing`                         | `workcell.parent` references an existing module contract                                        | error            | yes                        | core                     |
| `workcell.child_missing`                          | Declared `workcell.children` exist                                                              | error            | yes                        | core                     |
| `workcell.child_parent_mismatch`                  | Declared child's `workcell.parent` points back to this module                                   | error            | yes                        | core                     |
| `workcell.leaf_has_children`                      | Leaf workcells declare no children                                                              | error            | yes                        | core                     |
| `workcell.parent_cycle`                           | The parent chain forms no cycle                                                                 | error            | yes                        | core                     |
| `workcell.composite_owns_child_path`              | Non-leaf workcells do not own implementation paths inside descendants                           | error            | yes                        | core                     |
| `workcell.owns_path_overlap`                      | Leaf workcell `owns_paths` do not overlap across leaves                                         | error            | yes                        | core                     |
| `lease.*` (8 codes)                               | `.coad/leases.yml` schema, unique writes, leaf-only writes, scope inside ownership              | error (when present) | yes (opt-in by file)    | core                     |
| `workcell.budget` (informal — no `code=` set)     | When `workcell.context_budget` declared, actual files/lines/surfaces ≤ declared maxima          | error            | maybe (downgrade)          | core, severity=warning   |
| `release.version_unreadable` / `pyproject_unreadable` / `package_unreadable` / `changelog_unreadable` | When VERSION/CHANGELOG/pyproject/`__init__.py` present: they agree | error (opt-in) | no (validator self-check) | guidance (move out of `coad check .` for adopters) |
| `graph.proof_missing` / `graph.task_missing` / `graph.module_missing` / `graph.review_missing` / `graph.integration_missing` / `graph.readiness_proof_missing` / `graph.decomposition_task_missing` | Cross-contract reference integrity across goal/task/proof/review/integration | error (opt-in by file) | no (Evidence) | orchestration extension |
| `methodology_loop.{orient,scope,execute,prove,update_knowledge,handoff}_{missing,weak,unknown,skipped}` (~16 combos) | Per-phase evidence-trail aggregation                          | error/warning/info | no (Evidence)              | orchestration extension or DELETE |
| `handoff.{changed_files_missing,changed_files_extra,invalid,skipped}`                                            | `HANDOFF.changed_files` matches git diff                       | error/skipped | no (Evidence) | orchestration extension |
| `ledger_handoff.*` (12 codes)                                                                                    | `EXECUTION_LEDGER.json` ↔ `HANDOFF.md` cross-integrity         | error/skipped | no (Evidence) | orchestration extension |
| `proof_result.{handoff_*,ledger_*,task_missing,skipped}` (8 codes)                                               | Required proof commands appear as `pass` in handoff and ledger | error/skipped | no (Evidence) | orchestration extension |
| `proof_artifact.*` (~25 codes)                                                                                   | Proof artifact JSON / digest / size / payload provenance        | error/skipped | no (Evidence) | orchestration extension |
| `contract_update.{missing,empty_reason,extra,skipped}`                                                           | Changed methodology files appear in `HANDOFF.contract_updates`  | error/warning/skipped | no (Evidence) | orchestration extension |
| `task_scope.{write_scope_violation,forbidden_mutation,task_missing,skipped}`                                     | Git changed files inside `TASK_CONTRACT.write_scope`, not in `forbidden_mutations` | error/skipped | no (Evidence) | orchestration extension |
| `agent-guidance.failed` (synthetic)                                                                              | `AGENTS.md` exists, mentions `coad check`, mentions `MODULE_CONTRACT` | error | yes | core |
| `validation.error` (default for any uncategorized issue)                                                         | Catch-all                                                       | error            | yes (infra)                | core                     |

Summary counts: ~100 distinct `code` strings, of which ~25 are core
(everything in the table above the first Evidence row), the rest are Evidence
plumbing.

---

## B. Draft STANDARD.md (15 rules)

Every rule listed below already has an implementation. None is aspirational.

**COAD-001 — AGENTS.md exists and points at COAD.**
Statement: The repository root contains `AGENTS.md`. The file mentions
`coad check` and `MODULE_CONTRACT` (case-insensitive).
Schema: not schema-defined. Detected via file content.
Validator rule_id: `agent-guidance.failed` (in `agent_guidance.py`).
Severity: `error`.
Rationale: Without this file an agent following the public adoption link has
no entry point.

**COAD-002 — Repository declares at least one module contract.**
Statement: There is at least one Markdown file with YAML frontmatter
containing `kind: module_contract`.
Schema: `schema/module-contract.schema.json`, field `kind`.
Validator rule_id: `validation.module_contract_missing`.
Severity: `error`.
Rationale: A repo without any module contract has nothing for COAD to check.

**COAD-003 — Module contracts validate against the module-contract schema.**
Statement: Every `kind: module_contract` document passes
`module-contract.schema.json`.
Schema: `schema/module-contract.schema.json` (entire document).
Validator rule_id: `schema.violation`, `schema.not_found`,
`schema.unknown_contract_kind`.
Severity: `error`.
Rationale: The schema is the contract; without conformance the rest of the
checks have no foundation.

**COAD-004 — Module contract declares a workcell with a type.**
Statement: The frontmatter contains a `workcell` object with a non-empty
`type` field.
Schema: `module-contract.schema.json`, `workcell.type` (enum:
`project|composite|leaf`).
Validator rule_id: `semantic.workcell_missing`, `semantic.workcell_type_missing`.
Severity: `error`.
Rationale: Ownership boundary is the central abstraction.

**COAD-005 — Module contract declares at least one owns_path that exists.**
Statement: `workcell.owns_paths` lists ≥ 1 relative path inside the
repository, and each entry resolves to an existing file or directory.
Schema: `module-contract.schema.json`, `workcell.owns_paths`.
Validator rule_id: `semantic.owns_path_missing`,
`semantic.owns_path_invalid`, `semantic.owns_path_outside_repository`.
Severity: `error`.
Rationale: Without owned paths the contract is non-physical.

**COAD-006 — Module contract context_path resolves to a real directory with README.md and TODO.md.**
Statement: `workcell.context_path` (or fallback `module`) points to a real
directory inside the repo; that directory contains both `README.md` and
`TODO.md`.
Schema: `module-contract.schema.json`, `workcell.context_path`.
Validator rule_id: `module.context_outside_repository`, "module directory
does not exist", "module agent context is missing README.md/TODO.md".
Severity: `error`.
Rationale: Local agent context is the second half of the COAD adoption shape.

**COAD-007 — Module identifiers are unique repo-wide.**
Statement: No two `module_contract` documents declare the same `module:`.
Validator rule_id: `workcell.duplicate_module`.
Severity: `error`.
Rationale: Identifier collisions break the contract graph and lease checks.

**COAD-008 — Workcell tree is consistent.**
Statement: For every declared `workcell.parent`, the parent contract exists.
For every declared `workcell.children` entry, the child contract exists and
back-points to this parent. Leaf workcells declare no children. No cycle in
the parent chain. Non-leaf workcells do not own implementation paths owned by
descendants.
Validator rule_id: `workcell.parent_missing`, `workcell.child_missing`,
`workcell.child_parent_mismatch`, `workcell.leaf_has_children`,
`workcell.parent_cycle`, `workcell.composite_owns_child_path`.
Severity: `error`.
Rationale: This is what makes the tree mechanically meaningful.

**COAD-009 — Leaf owns_paths do not overlap.**
Statement: For any two leaf workcells, none of their `owns_paths` is a prefix
of the other.
Validator rule_id: `workcell.owns_path_overlap`.
Severity: `error`.
Rationale: Two leaves cannot share write authority over the same files.

**COAD-010 — Lease manifest, when present, references real leaf workcells and stays inside ownership.**
Statement: If `.coad/leases.yml` exists, it validates against the lease
manifest schema, every `workcell` reference resolves to a known leaf module
contract, `mode: write` is unique per workcell, and the lease `scope` stays
inside that workcell's `owns_paths`.
Schema: `schema/lease-manifest.schema.json`.
Validator rule_id: `lease.*` (8 codes).
Severity: `error` (opt-in: only when `.coad/leases.yml` exists).
Rationale: Active write-lease tracking is the only multi-agent safety story
COAD ships.

**COAD-011 — Module contract has at least one declared surface.**
Statement: `surface:` is a non-empty array.
Schema: `module-contract.schema.json`, `surface` (`minItems: 1`).
Validator rule_id: `semantic.surface_missing` plus the schema's own `minItems`.
Severity: `warning` (downgraded from `error`).
Rationale: A contract with no surface is rarely useful but not formally
broken; downgrade allows quick onboarding repos to ship.

**COAD-012 — Public surfaces have at least one declared consumer.**
Statement: For every `surface` with `visibility: public` and a `name`, at
least one `consumers[].uses[]` entry mentions the name.
Validator rule_id: `semantic.public_surface_without_consumer`.
Severity: `warning` (downgraded).
Rationale: Catches "documentation theater" without blocking adoption.

**COAD-013 — Module contract fields contain no placeholder strings.**
Statement: `purpose`, owners, surface fields, dependency reasons, consumer
paths, invariant rules, and surface/invariant proof targets/commands do not
match common placeholder patterns (`TODO`, `TBD`, `<replace-me>`,
`Your module`, etc.).
Validator rule_id: `semantic.placeholder`, `semantic.proof_placeholder`,
`semantic.purpose_too_generic`.
Severity: `warning` (downgraded; `purpose_too_generic` becomes `info`).
Rationale: Placeholder detection is heuristic; useful as a nudge, not as a
hard gate.

**COAD-014 — Module README.md and TODO.md contain meaningful content.**
Statement: For each module contract, the README.md and TODO.md in the
resolved context directory contain at least one non-heading non-placeholder
line.
Validator rule_id: `semantic.context_file_empty`.
Severity: `warning` (downgraded).
Rationale: Empty stubs satisfy the file-existence check (COAD-006) without
giving an agent anything to read; warning prevents stub-driven adoption.

**COAD-015 — Workcell context budgets, when declared, are respected.**
Statement: If `workcell.context_budget` declares any of
`max_files`, `max_source_lines`, `max_contract_lines`, `max_readme_lines`,
`max_todo_lines`, `max_surfaces`, `max_invariants`, the actuals computed by
the validator do not exceed those caps unless covered by a
`workcell.budget_exceptions` entry with a non-empty `reason`.
Schema: `module-contract.schema.json`, `workcell.context_budget`.
Validator rule_id: workcell budget messages (no stable `code=`; will be
codified as `workcell.budget_exceeded` in Phase 2).
Severity: `warning` (downgraded from error).
Rationale: Budget breaches are a smell, not a violation. The team has not
seen evidence that a hard fail is justified.

Five `error`-level rules cover the mechanical shape (COAD-001 through
COAD-005 and COAD-006/007). Three `error`-level rules cover the multi-leaf
graph (COAD-008/009/010). Seven `warning`-level rules cover quality nudges.
This satisfies the "≥ 3 rules at warning" acceptance criterion.

Rules **not** in v2 standard:
- `release.*` becomes opt-in *for the COAD repo itself*, not part of
  `coad check .` for adopters.
- The entire `graph.*` family (cross-contract references for goal/task/proof
  /review/integration), the `methodology_loop.*` family, `handoff.*`,
  `ledger_handoff.*`, `proof_result.*`, `proof_artifact.*`,
  `contract_update.*`, and `task_scope.*` move to the orchestration extension
  (see section D).

---

## C. File Move and Delete Map

| Current path                          | Action                  | Target path                                                        |
| ------------------------------------- | ----------------------- | ------------------------------------------------------------------ |
| `README.md`                           | keep (rewrite ≤ 200 LOC) | `README.md`                                                        |
| `STANDARD.md`                         | create (Phase 2)        | `STANDARD.md`                                                      |
| `AGENT_ONBOARDING.md`                 | keep (rewrite ≤ 80 LOC) | `AGENT_ONBOARDING.md`                                              |
| `AGENTS.md`                           | keep                    | `AGENTS.md` (mention STANDARD.md instead of COAD_PROJECT_STANDARD) |
| `CHANGELOG.md`                        | keep                    | `CHANGELOG.md`                                                     |
| `SPEC.md`                             | move (history)          | `docs/archive/SPEC.md.v0.7.7`                                      |
| `PRINCIPLES.md`                       | move (rationale)        | `docs/archive/PRINCIPLES.md.v0.7.7`                                |
| `AGENT_FLOW.md`                       | move (history)          | `docs/archive/AGENT_FLOW.md.v0.7.7`                                |
| `COAD_PROJECT_STANDARD.md`            | move (replaced)         | `docs/archive/COAD_PROJECT_STANDARD.md.v0.7.7`                     |
| `ADOPTION.md`                         | move (history)          | `docs/archive/ADOPTION.md.v0.7.7`                                  |
| `GETTING_STARTED.md`                  | move (replaced by README + AGENT_ONBOARDING) | `docs/archive/GETTING_STARTED.md.v0.7.7`     |
| `GLOSSARY.md`                         | move (low value)        | `docs/archive/GLOSSARY.md.v0.7.7`                                  |
| `TODO.md`                             | keep (root TODO)        | `TODO.md`                                                          |
| `VERSION`                             | keep                    | `VERSION`                                                          |
| `COAD_PROFILE.json`                   | move (Evidence)         | `docs/archive/COAD_PROFILE.json.v0.7.7`                            |
| `docs/agent-decision-rules.md`        | move                    | `docs/archive/`                                                    |
| `docs/agent-integration.md`           | move                    | `docs/archive/`                                                    |
| `docs/anti-patterns.md`               | move                    | `docs/archive/`                                                    |
| `docs/adoption-smoke-tests.md`        | keep (will be needed in Phase 3) | `docs/adoption-smoke-tests.md`                          |
| `docs/artifact-export.md`             | move (Evidence)         | `docs/archive/`                                                    |
| `docs/attestation-bundle.md`          | move (Evidence)         | `docs/archive/`                                                    |
| `docs/conformance-profile.md`         | move (Evidence)         | `docs/archive/`                                                    |
| `docs/context-packs.md`               | move (Evidence)         | `docs/archive/`                                                    |
| `docs/contract-graph.md`              | move (Evidence)         | `docs/archive/`                                                    |
| `docs/demo-transcripts.md`            | keep (linked from README) | `docs/demo-transcripts.md`                                       |
| `docs/execution-ledger.md`            | move (Evidence)         | `docs/archive/`                                                    |
| `docs/landscape.md`                   | keep (linked from README) | `docs/landscape.md`                                              |
| `docs/maturity-model.md`              | move                    | `docs/archive/`                                                    |
| `docs/module-contract-checklist.md`   | keep (will reference STANDARD.md) | `docs/module-contract-checklist.md`                      |
| `docs/normative-language.md`          | move (replaced)         | `docs/archive/`                                                    |
| `docs/orchestration-model.md`         | move (Evidence)         | `docs/archive/`                                                    |
| `docs/policy-enforcement.md`          | move (Evidence)         | `docs/archive/`                                                    |
| `docs/proof-matrix.md`                | move (Evidence)         | `docs/archive/`                                                    |
| `docs/release-gates.md`               | move                    | `docs/archive/`                                                    |
| `docs/report-versioning.md`           | move                    | `docs/archive/`                                                    |
| `docs/tool-output-schemas.md`         | move                    | `docs/archive/`                                                    |
| `docs/validator.md`                   | keep (rewrite to match STANDARD) | `docs/validator.md`                                     |
| `docs/workcells.md`                   | merge into STANDARD.md or keep trimmed | `docs/workcells.md` (trimmed)                       |
| `docs/README.md`                      | keep (rewrite as docs/archive index) | `docs/README.md`                                      |
| `contracts/`                          | move (Evidence)         | `docs/archive/contracts/`                                          |
| `playbooks/`                          | move                    | `docs/archive/playbooks/`                                          |
| `templates/`                          | keep (used by onboarding) but trim to module-contract + README + TODO templates | `templates/`         |
| `schema/conformance-profile.schema.json` | move to extensions   | `schema/extensions/`                                               |
| `schema/execution-ledger.schema.json` | move to extensions      | `schema/extensions/`                                               |
| `schema/goal-contract.schema.json`    | move to extensions      | `schema/extensions/`                                               |
| `schema/handoff-contract.schema.json` | move to extensions      | `schema/extensions/`                                               |
| `schema/integration-contract.schema.json` | move to extensions  | `schema/extensions/`                                               |
| `schema/proof-artifact.schema.json`   | move to extensions      | `schema/extensions/`                                               |
| `schema/proof-contract.schema.json`   | move to extensions      | `schema/extensions/`                                               |
| `schema/review-contract.schema.json`  | move to extensions      | `schema/extensions/`                                               |
| `schema/task-contract.schema.json`    | move to extensions      | `schema/extensions/`                                               |
| `schema/release-manifest.json` / `.schema.json` | move to extensions | `schema/extensions/`                                          |
| `schema/report-manifest.json` / `.schema.json`  | move to extensions | `schema/extensions/`                                          |
| `schema/reports/*.schema.json`        | move to extensions      | `schema/extensions/reports/`                                       |
| `schema/lease-manifest.schema.json`   | keep                    | `schema/lease-manifest.schema.json`                                |
| `schema/module-contract.schema.json`  | keep (revised in Phase 2) | `schema/module-contract.schema.json`                             |
| `schema/README.md`                    | keep (rewritten)        | `schema/README.md`                                                 |
| `examples/minimal/`                   | shrink                  | `examples/minimal/` (drop GOAL/TASK/PROOF/HANDOFF/REVIEW/INTEGRATION/EXECUTION_LEDGER) |
| `examples/before-after/`              | keep                    | `examples/before-after/`                                           |
| `examples/onboarding/`                | keep (verify still passes) | `examples/onboarding/`                                          |
| `examples/parallel-work/`             | keep (lease demo)       | `examples/parallel-work/`                                          |
| `examples/invalid/`                   | keep                    | `examples/invalid/`                                                |
| `project-contracts/`                  | shrink                  | `project-contracts/` (keep one self-contract per real workcell; drop the Evidence stack) |
| `tools/coad-validator/src/coad_validator/{ledger,schedule,policy,status,attest,profile,drift,graph_report,artifact_export,proof_matrix,handoff_integrity,ledger_handoff_integrity,proof_result_integrity,proof_artifact_integrity,contract_update_integrity,task_scope_integrity,methodology_loop,release_metadata,graph,graph_index}.py` + matching `_cli.py` siblings | move to extension | `tools/coad-validator/src/coad_validator/extensions/evidence/` |
| `tools/coad-validator/src/coad_validator/{frontmatter,schema,validate,model,module_context,ownership,workcell_graph,workcell_budget,semantic_quality,lease_manifest,agent_guidance,text_io,cli,coad_cli,check,report,report_sources}.py` | keep (core)        | unchanged                                                          |
| `tools/coad-validator/tests/{test_validator,test_check}.py` | keep            | unchanged                                                          |
| `tools/coad-validator/tests/{test_ledger,test_schedule,test_policy,test_status,test_attest,test_profile,test_drift,test_export,test_graph_report,test_graph_index,test_proof_matrix,test_pack,test_report_schemas,test_report_versioning}.py` | move with extension | `tools/coad-validator/tests/extensions/evidence/` |

After this move, the root contains exactly five Markdown files (README,
STANDARD, AGENT_ONBOARDING, CHANGELOG, AGENTS) plus VERSION and TODO.md.

---

## D. Evidence: In-Tree Extension vs. Separate Package

Two options:

**Option 1 — in-tree extension module (recommended).**
Keep everything in `tools/coad-validator/`. Add
`src/coad_validator/extensions/evidence/` with its own `__init__.py` and
public entry. The Evidence checks are activated by `report_sources.py` only
when a target repository contains any of `goal_contract`, `task_contract`,
`proof_contract`, `handoff_contract`, `integration_contract`,
`review_contract`, or a `.coad/EXECUTION_LEDGER.json`. That detection logic
already exists in `check.py::EXECUTION_CONTRACT_KINDS`; we just relocate the
imports behind a feature predicate and a dedicated package.

**Option 2 — separate `coad-evidence` package.**
Split into its own `pyproject.toml` under `tools/coad-evidence/` or a
separate repo. The validator would advertise a plugin entry point or import
the package only if installed.

I recommend **Option 1**. Reasons in three points:

1. Zero external users today — splitting now buys nothing and creates two
   release cadences, two CHANGELOGs, and a cross-package import shim.
2. The Core/Evidence boundary is already a Python-import boundary inside one
   process: a directory is a sufficient mechanical seam. We can always
   promote to a separate package later when (and if) an external user asks
   for Core-only install.
3. Tests and fixtures cross the boundary today (the Evidence reports import
   from `validate.py`, `model.py`, `graph_index.py`). Extracting them into a
   separate distribution requires API-stability promises we are not ready
   to make on a 0.x project.

If the user prefers Option 2, the change is a Phase 2.5 follow-up that is
mechanical given Option 1 is already a clean directory.

---

## E. Do Not Touch

These pieces work, are checkable, and are part of the standard. Leave the
implementation untouched in Phase 2:

- `frontmatter.py` — Markdown frontmatter discovery and the `_SKIP_DIRS` set.
- `schema.py` — JSON Schema validation pipeline (Draft 2020-12, sorted
  errors). Only the schema files change in Phase 2, not the validator.
- `validate.py::validate_path` — composition root for Core checks (will lose
  one `validate_graph` call when graph moves to Evidence, otherwise
  unchanged).
- `model.py` — `ContractDocument`, `ValidationIssue`, `ValidationFailure`
  (severity field already exists; Phase 2 just starts setting it to
  `warning`/`info`).
- `module_context.py`, `ownership.py` — context-path resolution and
  owns_path resolution. These power COAD-005, COAD-006, COAD-009.
- `workcell_graph.py` — parent/child/cycle/overlap detection. Powers
  COAD-007, COAD-008, COAD-009.
- `lease_manifest.py` — the only multi-agent safety story we keep.
- `cli.py` — `coad-validate` legacy entry point. Keeps `--no-graph`.
- `coad_cli.py` — `coad check` public entry. Phase 2 will only change which
  sources it activates by default for adopter repos.
- `agent_guidance.py` — COAD-001 implementation; tiny and stable.
- `semantic_quality.py` — COAD-011/012/013/014 implementation. Severity
  changes touch this file but logic stays.
- `workcell_budget.py` — COAD-015 implementation.
- `text_io.py` — UTF-8 read helper.
- `report.py` — `versioned_report` wrapper.
- `examples/before-after/` — demoes the public adoption gate from README.
- `examples/onboarding/` — minimal passing shape for AGENT_ONBOARDING.

---

## F. Risks

1. **Self-dogfooding breaks.** `project-contracts/` declares a deep
   workcell tree with Evidence-style contracts. `coad check .` on the COAD
   repo itself will trip the Evidence sources today. After Phase 2 we will
   either (a) keep Evidence enabled when COAD checks itself and tolerate
   that those contracts use the extension layer, or (b) shrink
   `project-contracts/` to a single root module contract. Plan: (a) for
   Phase 2, optionally (b) later.

2. **External agents reading `coad check . --format json` see a different
   `checks[]` shape.** The output schema is
   `schema/reports/check-report.schema.json`. Today no external user has
   been identified. We will bump the validator to 0.8.0 to signal the
   break; we will not promise backwards compatibility on the JSON envelope
   for v2 since no contract was ever published.

3. **Tests for the Evidence stack outnumber tests for Core.** Of the 16
   `test_*.py` files, only `test_validator.py` and `test_check.py`
   exclusively cover Core. The risk is that re-categorizing the rest as
   "extension tests" hides regressions in moves. Mitigation: keep all those
   tests passing under the new path; `xfail` only when the test genuinely
   asserts Evidence behavior that is not promised by the standard.

4. **`release_metadata` rule.** This was added to enforce consistency of the
   COAD package's own VERSION/CHANGELOG/pyproject. It runs against any
   adopter repo as soon as those three files exist together. That is
   overreach. Plan: remove from the default check pipeline in Phase 2; keep
   as an internal CI step inside `tools/coad-validator/` only.

5. **Documentation references between files.** `AGENTS.md`, `README.md`,
   `AGENT_ONBOARDING.md`, `docs/validator.md`, `templates/`, and several
   examples cross-link to each other and to soon-archived files
   (`COAD_PROJECT_STANDARD.md`, `AGENT_FLOW.md`, `docs/workcells.md`,
   `GETTING_STARTED.md`). Phase 2 must rewrite each link or the public
   adoption story regresses. Mitigation: grep for every archived filename
   before committing Phase 2.

6. **`.coad/leases.yml` validation breaks if module-contract schema becomes
   too permissive.** Lease validation uses `workcell.owns_paths` and
   `workcell.type`. We must keep both required in the slimmed schema.

7. **`AGENT_ONBOARDING.md` ≤ 80 lines is tight.** The current file is 164
   lines and already factored down. The rewrite will drop install
   alternatives, retain the public `uvx` one-liner, the four-step adoption
   recipe, and a minimal `AGENTS.md` block. Cutting beyond that risks
   making the agent perform repository edits without enough rules.

---

End of Phase 1 report.
