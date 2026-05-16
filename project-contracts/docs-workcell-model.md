---
schema_version: 1
kind: module_contract
module: docs/workcell-model
level: subsystem
layer: methodology
purpose: Explain workcell sizing, authority, module contracts, and the semantic checklist.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: docs
  context_path: docs
  children: []
  owns_paths:
    - docs/workcells.md
    - docs/module-contract-checklist.md
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
  orchestrator: docs
  read_agents: many_allowed
surface:
  - name: WorkcellMethodologyDocs
    kind: documentation-api
    visibility: public
    contract: Defines the workcell model, context budgets, authority, and module contract quality bar.
    proof:
      kind: static-check
      target: docs/workcells.md docs/module-contract-checklist.md
      command: coad check .
dependencies:
  internal:
    - module: contracts
      scope: module contract semantics
      reason: These docs explain the module/workcell contract.
    - module: tools/coad-validator
      scope: budget validation behavior
      reason: Budget semantics must match `coad check .`.
  external: []
consumers:
  - path: README.md
    uses:
      - WorkcellMethodologyDocs
invariants: []
verification:
  pre_change:
    - coad check .
  full:
    - coad check .
---

# docs/workcell-model

Owns the public explanation of COAD workcell boundaries and contract quality.
