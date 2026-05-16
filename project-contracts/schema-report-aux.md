---
schema_version: 1
kind: module_contract
module: schema/report-aux
level: subsystem
layer: tooling-contract
purpose: Maintain schemas for auxiliary reports, exports, profiles, policies, and errors.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: schema
  context_path: schema
  children: []
  owns_paths:
    - schema/reports/attestation-report.schema.json
    - schema/reports/context-pack.schema.json
    - schema/reports/drift-report.schema.json
    - schema/reports/export-report.schema.json
    - schema/reports/pack-error.schema.json
    - schema/reports/policy-report.schema.json
    - schema/reports/profile-report.schema.json
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
  - name: AuxiliaryReportSchemas
    kind: schema-set
    visibility: public
    contract: Validates auxiliary COAD report and export payloads.
    proof:
      kind: schema
      target: schema/reports
      command: jq empty schema/*.json schema/reports/*.json
dependencies:
  internal:
    - module: tools/coad-validator
      scope: report payloads
      reason: Schemas must match validator report builders.
  external: []
consumers:
  - path: tools/coad-validator/tests/test_report_schemas.py
    uses:
      - AuxiliaryReportSchemas
invariants: []
verification:
  pre_change:
    - jq empty schema/*.json schema/reports/*.json
  full:
    - uv run --locked pytest
    - coad check .
---

# schema/report-aux

Owns schemas for auxiliary report and export payloads.
