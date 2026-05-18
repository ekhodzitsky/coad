---
schema_version: 1
kind: module_contract
module: validator/bundled-report-schemas-core
level: subsystem
layer: tooling
purpose: Keep bundled core report schemas in sync with canonical report schemas.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: tools/coad-validator
  context_path: tools/coad-validator
  children: []
  owns_paths:
    - tools/coad-validator/src/coad_validator/schema/reports/agent-guidance-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/check-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/contract-update-integrity-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/graph-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/handoff-integrity-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/ledger-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/proof-matrix.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/proof-result-integrity-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/schedule-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/status-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/task-scope-integrity-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/validation-report.schema.json
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
  - name: BundledCoreReportSchemas
    kind: schema-set
    visibility: internal
    contract: Provides packaged schemas for core report payloads.
    proof:
      kind: schema
      target: tools/coad-validator/src/coad_validator/schema/reports
      command: jq empty tools/coad-validator/src/coad_validator/schema/*.json tools/coad-validator/src/coad_validator/schema/reports/*.json
dependencies:
  internal:
    - module: schema/report-core
      scope: canonical report schemas
      reason: Bundled report schemas must match canonical files.
  external: []
consumers:
  - path: tools/coad-validator/tests/test_report_schemas.py
    uses:
      - BundledCoreReportSchemas
invariants: []
verification:
  pre_change:
    - jq empty tools/coad-validator/src/coad_validator/schema/*.json tools/coad-validator/src/coad_validator/schema/reports/*.json
  full:
    - uv run --locked pytest
    - coad check .
---

# validator/bundled-report-schemas-core

Owns bundled schemas for core reports.
