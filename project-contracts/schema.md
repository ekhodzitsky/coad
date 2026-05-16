---
schema_version: 1
kind: module_contract
module: schema
level: root
layer: tooling-contract
purpose: Define executable JSON schemas for contracts, workcell authority fields, reports, and release manifests.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: project
  children: []
  owns_paths:
    - schema/
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
      reason: Schema workcell owns contract and report schemas together until report schemas justify a child workcell.
    - metric: max_source_lines
      reason: JSON schemas are verbose executable contracts; split report schemas when schema maintenance becomes parallel.
authority:
  write_policy: single_active_write_lease
  orchestrator: project
  read_agents: many_allowed
  migration_lease_required:
    - cross-workcell write
    - public surface migration
surface:
  - name: ContractSchemas
    kind: schema-set
    visibility: public
    contract: Validates COAD contract frontmatter, workcell authority fields, and report payloads.
    proof:
      kind: schema
      target: schema/*.json schema/reports/*.json
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
  - path: docs/tool-output-schemas.md
    uses:
      - ContractSchemas
invariants:
  - id: schemas-parse-as-json
    rule: Every schema and manifest JSON file must parse before release.
    proof:
      kind: schema
      target: schema
      command: jq empty schema/*.json schema/reports/*.json
verification:
  pre_change:
    - jq empty schema/*.json schema/reports/*.json
  full:
    - uv run --locked pytest
    - coad check .
agent_policy:
  allowed_mutations:
    - Add backward-compatible schema fields with tests and documentation.
  forbidden_mutations:
    - Break existing report payloads without updating schema versioning docs.
  escalation:
    - Required field addition
    - Report schema compatibility break
---

# schema

The schema module owns executable COAD schema contracts.
