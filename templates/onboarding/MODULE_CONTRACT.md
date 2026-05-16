---
schema_version: 1
kind: module_contract
module: replace-with-module-path
level: root
layer: replace-with-layer
purpose: Replace with the module ownership boundary agents must preserve.
status: pilot
owners:
  - replace-with-owner
workcell:
  type: leaf
  parent: replace-with-parent-or-empty
  children: []
  owns_paths:
    - replace-with-module-path/
  context_budget:
    max_files: 12
    max_source_lines: 1500
    max_contract_lines: 180
    max_readme_lines: 120
    max_todo_lines: 80
    max_surfaces: 8
    max_invariants: 8
authority:
  write_policy: single_active_write_lease
  orchestrator: replace-with-owner-or-parent
  read_agents: many_allowed
  migration_lease_required:
    - cross-workcell write
    - public surface migration
surface:
  - name: ReplaceWithSurface
    kind: service
    visibility: internal
    contract: Replace with the stable promise this surface makes.
    proof:
      kind: unit-test
      target: replace.with.test.target
      command: replace with test command
dependencies:
  internal: []
  external: []
consumers: []
invariants:
  - id: replace-with-invariant-id
    rule: Replace with the invariant agents must preserve.
    proof:
      kind: unit-test
      target: replace.with.invariant.test
      command: replace with test command
verification:
  pre_change:
    - replace with focused check
  full:
    - replace with full check
agent_policy:
  allowed_mutations:
    - Replace with safe changes agents may make.
  forbidden_mutations:
    - Replace with changes agents must not make silently.
  escalation:
    - Replace with changes that require human or lead-agent approval.
---

# replace-with-module-path

Replace with a short description of what this module owns.
