---
schema_version: 1
kind: module_contract
module: schema/contracts
level: subsystem
layer: tooling-contract
purpose: Maintain JSON schemas for COAD contract documents.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: schema
  context_path: schema
  children: []
  owns_paths:
    - schema/extensions/execution-ledger.schema.json
    - schema/extensions/goal-contract.schema.json
    - schema/extensions/handoff-contract.schema.json
    - schema/extensions/integration-contract.schema.json
    - schema/module-contract.schema.json
    - schema/extensions/proof-artifact.schema.json
    - schema/extensions/proof-contract.schema.json
    - schema/extensions/review-contract.schema.json
    - schema/extensions/task-contract.schema.json
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
  orchestrator: schema
  read_agents: many_allowed
surface:
  - name: ContractSchemas
    kind: schema-set
    visibility: public
    contract: Validates COAD contract frontmatter and execution ledgers.
    proof:
      kind: schema
      target: schema/*-contract.schema.json schema/extensions/execution-ledger.schema.json
      command: jq empty schema/*.json schema/reports/*.json
dependencies:
  internal:
    - module: contracts
      scope: contract semantics
      reason: Schemas execute the human-readable contract specs.
  external: []
consumers:
  - path: tools/coad-validator
    uses:
      - ContractSchemas
invariants: []
verification:
  pre_change:
    - jq empty schema/*.json schema/reports/*.json
  full:
    - uv run --locked pytest
    - coad check .
---

# schema/contracts

Owns machine-readable schemas for COAD contract files.
