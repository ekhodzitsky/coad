---
schema_version: 1
kind: module_contract
module: templates/contracts
level: subsystem
layer: methodology
purpose: Maintain reusable contract templates for COAD artifacts.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: templates
  context_path: templates
  children: []
  owns_paths:
    - templates/GOAL_CONTRACT.md
    - templates/HANDOFF.md
    - templates/INTEGRATION.md
    - templates/MODULE_CONTRACT.md
    - templates/PROOF.md
    - templates/REVIEW.md
    - templates/TASK_CONTRACT.md
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
  orchestrator: templates
  read_agents: many_allowed
surface:
  - name: ContractTemplates
    kind: template-set
    visibility: public
    contract: Provides starter templates for COAD contract artifacts.
    proof:
      kind: static-check
      target: templates
      command: coad check .
dependencies:
  internal:
    - module: contracts
      scope: contract semantics
      reason: Templates must match human-readable specs.
    - module: schema
      scope: frontmatter shape
      reason: Templates should stay close to executable schemas.
  external: []
consumers:
  - path: GETTING_STARTED.md
    uses:
      - ContractTemplates
invariants: []
verification:
  pre_change:
    - coad check .
  full:
    - coad check .
---

# templates/contracts

Owns reusable templates for COAD contract artifacts.
