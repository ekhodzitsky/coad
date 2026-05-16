---
schema_version: 1
kind: module_contract
module: schema
level: root
layer: tooling-contract
purpose: Define executable JSON schemas for contracts, reports, and release manifests.
status: pilot
owners:
  - validator-maintainers
surface:
  - name: ContractSchemas
    kind: schema-set
    visibility: public
    contract: Validates COAD contract frontmatter and report payloads.
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
