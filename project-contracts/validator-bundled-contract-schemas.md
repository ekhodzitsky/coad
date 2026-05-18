---
schema_version: 1
kind: module_contract
module: validator/bundled-contract-schemas
level: subsystem
layer: tooling
purpose: Keep bundled contract schemas in sync with canonical repository schemas.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: tools/coad-validator
  context_path: tools/coad-validator
  children: []
  owns_paths:
    - tools/coad-validator/src/coad_validator/schema/execution-ledger.schema.json
    - tools/coad-validator/src/coad_validator/schema/goal-contract.schema.json
    - tools/coad-validator/src/coad_validator/schema/handoff-contract.schema.json
    - tools/coad-validator/src/coad_validator/schema/integration-contract.schema.json
    - tools/coad-validator/src/coad_validator/schema/module-contract.schema.json
    - tools/coad-validator/src/coad_validator/schema/proof-artifact.schema.json
    - tools/coad-validator/src/coad_validator/schema/proof-contract.schema.json
    - tools/coad-validator/src/coad_validator/schema/review-contract.schema.json
    - tools/coad-validator/src/coad_validator/schema/task-contract.schema.json
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
  orchestrator: tools/coad-validator
  read_agents: many_allowed
surface:
  - name: BundledContractSchemas
    kind: schema-set
    visibility: internal
    contract: Provides installable schemas for contract validation when no local schema dir is supplied.
    proof:
      kind: schema
      target: tools/coad-validator/src/coad_validator/schema
      command: jq empty tools/coad-validator/src/coad_validator/schema/*.json tools/coad-validator/src/coad_validator/schema/reports/*.json
dependencies:
  internal:
    - module: schema/contracts
      scope: canonical schemas
      reason: Bundled schemas must match canonical schemas.
  external: []
consumers:
  - path: tools/coad-validator/src/coad_validator/validate.py
    uses:
      - BundledContractSchemas
invariants: []
verification:
  pre_change:
    - jq empty tools/coad-validator/src/coad_validator/schema/*.json tools/coad-validator/src/coad_validator/schema/reports/*.json
  full:
    - uv run --locked pytest
    - coad check .
---

# validator/bundled-contract-schemas

Owns bundled contract schemas shipped with the validator package.
