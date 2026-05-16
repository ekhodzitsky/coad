---
schema_version: 1
kind: module_contract
module: templates
level: root
layer: methodology
purpose: Provide copyable contract and onboarding templates.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: project
  children: []
  owns_paths:
    - templates/
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
      reason: Template family is temporarily kept together so onboarding stays coherent while the starter set is still changing.
authority:
  write_policy: single_active_write_lease
  orchestrator: project
  read_agents: many_allowed
  migration_lease_required:
    - cross-workcell write
    - public surface migration
surface:
  - name: ContractTemplates
    kind: template-set
    visibility: public
    contract: Gives agents starting points without being treated as live contracts.
    proof:
      kind: static-check
      target: templates
      command: coad check .
dependencies:
  internal:
    - module: contracts
      scope: template semantics
      reason: Templates must match canonical contract specs.
    - module: schema
      scope: frontmatter shape
      reason: Templates should remain close to executable schemas.
  external: []
consumers:
  - path: GETTING_STARTED.md
    uses:
      - ContractTemplates
  - path: ADOPTION.md
    uses:
      - ContractTemplates
invariants:
  - id: templates-are-not-live-contracts
    rule: Repository validation skips templates so placeholders do not become contract errors.
    proof:
      kind: static-check
      target: tools/coad-validator/src/coad_validator/frontmatter.py
      command: uv run --locked pytest tests/test_validator.py
  - id: templates-include-workcell-authority
    rule: Module contract templates include workcell and authority fields without making adoption heavier than `coad check .`.
    proof:
      kind: static-check
      target: templates/MODULE_CONTRACT.md templates/onboarding/MODULE_CONTRACT.md
      command: rg "workcell:|authority:" templates/MODULE_CONTRACT.md templates/onboarding/MODULE_CONTRACT.md
verification:
  pre_change:
    - uv run --locked pytest tests/test_validator.py
  full:
    - uv run --locked pytest
    - coad check .
agent_policy:
  allowed_mutations:
    - Improve starter templates while keeping the onboarding flow copy-pasteable.
  forbidden_mutations:
    - Add required placeholders that prevent the template from being understandable.
  escalation:
    - Template change that requires validator schema changes
---

# templates

The templates module owns copyable COAD starting points.
