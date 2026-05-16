---
schema_version: 1
kind: module_contract
module: contracts
level: root
layer: methodology
purpose: Define the canonical COAD contract types and their semantics.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: project
  children: []
  owns_paths:
    - contracts/
  context_budget:
    max_files: 12
    max_source_lines: 1500
    max_contract_lines: 180
    max_readme_lines: 120
    max_todo_lines: 80
authority:
  write_policy: single_active_write_lease
  orchestrator: project
  read_agents: many_allowed
  migration_lease_required:
    - cross-workcell write
    - public surface migration
surface:
  - name: ContractTypeSpecs
    kind: documentation-api
    visibility: public
    contract: Defines the meaning and required content of COAD contract types.
    proof:
      kind: static-check
      target: contracts/*.md
      command: coad check .
dependencies:
  internal: []
  external: []
consumers:
  - path: schema
    uses:
      - ContractTypeSpecs
  - path: templates
    uses:
      - ContractTypeSpecs
  - path: docs
    uses:
      - ContractTypeSpecs
invariants:
  - id: specs-remain-normative
    rule: Contract specs define methodology semantics without adding hidden CLI requirements.
    proof:
      kind: static-check
      target: contracts/*.md
      command: coad check .
verification:
  pre_change:
    - coad check .
  full:
    - uv run --locked pytest
    - coad check .
agent_policy:
  allowed_mutations:
    - Clarify contract semantics while keeping schemas and templates aligned.
  forbidden_mutations:
    - Add new required ceremony without updating adoption docs and schemas.
  escalation:
    - New contract type
    - Breaking change to an existing contract type
---

# contracts

The contracts module owns the human-readable contract semantics for COAD.
