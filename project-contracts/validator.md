---
schema_version: 1
kind: module_contract
module: tools/coad-validator
level: root
layer: tooling
purpose: Implement the lightweight `coad check .` utility and internal report builders.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: project
  children: []
  owns_paths:
    - tools/coad-validator/
  context_budget:
    max_files: 12
    max_source_lines: 1500
    max_contract_lines: 180
    max_readme_lines: 120
    max_todo_lines: 80
    max_surfaces: 8
    max_invariants: 8
  budget_exceptions:
    - metric: max_files
      reason: Validator package includes CLI, reports, schemas, and tests; split report builders into child workcells after the public check surface stabilizes.
    - metric: max_source_lines
      reason: Current line count includes validator tests and bundled report schemas; keep visible until the validator module is decomposed.
authority:
  write_policy: single_active_write_lease
  orchestrator: project
  read_agents: many_allowed
  migration_lease_required:
    - cross-workcell write
    - public surface migration
surface:
  - name: coad check
    kind: cli
    visibility: public
    contract: Runs the progressive COAD methodology compliance check.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests/test_check.py
      command: uv run --locked pytest tests/test_check.py
dependencies:
  internal:
    - module: schema
      scope: validation schemas
      reason: The checker executes schema validation.
    - module: docs
      scope: public behavior
      reason: CLI behavior must match adoption docs.
  external:
    - name: jsonschema
      scope: Draft 2020-12 validation
      reason: Contract and report schemas need standard validation.
    - name: pyyaml
      scope: Markdown frontmatter parsing
      reason: Contract files use YAML frontmatter.
consumers:
  - path: .github/workflows/ci.yml
    uses:
      - coad check
  - path: GETTING_STARTED.md
    uses:
      - coad check
invariants:
  - id: one-public-command
    rule: The package exposes only the `coad` console script and the public subcommand is `check`.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests/test_check.py
      command: uv run --locked pytest tests/test_check.py
verification:
  pre_change:
    - uv run --locked pytest tests/test_check.py
  full:
    - uv run --locked pytest
    - coad check .
agent_policy:
  allowed_mutations:
    - Improve checker behavior while preserving one-line text output.
  forbidden_mutations:
    - Add new public console scripts without changing the methodology contract.
  escalation:
    - New public CLI command
    - Check semantics that block the two-minute onboarding path
---

# tools/coad-validator

The validator module owns the executable `coad check .` integration surface.
