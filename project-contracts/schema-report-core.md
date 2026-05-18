---
schema_version: 1
kind: module_contract
module: schema/report-core
level: subsystem
layer: tooling-contract
purpose: Maintain schemas for core validator reports used by `coad check .`.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: schema
  context_path: schema
  children: []
  owns_paths:
    - schema/reports/agent-guidance-report.schema.json
    - schema/reports/check-report.schema.json
    - schema/reports/graph-report.schema.json
    - schema/reports/handoff-integrity-report.schema.json
    - schema/reports/ledger-report.schema.json
    - schema/reports/proof-matrix.schema.json
    - schema/reports/schedule-report.schema.json
    - schema/reports/status-report.schema.json
    - schema/reports/validation-report.schema.json
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
  - name: CoreReportSchemas
    kind: schema-set
    visibility: public
    contract: Validates core COAD report payloads emitted by the validator.
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
      - CoreReportSchemas
invariants: []
verification:
  pre_change:
    - jq empty schema/*.json schema/reports/*.json
  full:
    - uv run --locked pytest
    - coad check .
---

# schema/report-core

Owns schemas for core report payloads.
