---
schema_version: 1
kind: module_contract
module: validator/bundled-report-schemas-aux
level: subsystem
layer: tooling
purpose: Keep bundled auxiliary report schemas in sync with canonical report schemas.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: tools/coad-validator
  context_path: tools/coad-validator
  children: []
  owns_paths:
    - tools/coad-validator/src/coad_validator/schema/reports/attestation-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/context-pack.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/drift-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/export-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/pack-error.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/policy-report.schema.json
    - tools/coad-validator/src/coad_validator/schema/reports/profile-report.schema.json
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
  - name: BundledAuxiliaryReportSchemas
    kind: schema-set
    visibility: internal
    contract: Provides packaged schemas for auxiliary report payloads.
    proof:
      kind: schema
      target: tools/coad-validator/src/coad_validator/schema/reports
      command: jq empty tools/coad-validator/src/coad_validator/schema/*.json tools/coad-validator/src/coad_validator/schema/reports/*.json
dependencies:
  internal:
    - module: schema/report-aux
      scope: canonical report schemas
      reason: Bundled report schemas must match canonical files.
  external: []
consumers:
  - path: tools/coad-validator/tests/test_report_schemas.py
    uses:
      - BundledAuxiliaryReportSchemas
invariants: []
verification:
  pre_change:
    - jq empty tools/coad-validator/src/coad_validator/schema/*.json tools/coad-validator/src/coad_validator/schema/reports/*.json
  full:
    - uv run --locked pytest
    - coad check .
---

# validator/bundled-report-schemas-aux

Owns bundled schemas for auxiliary reports.
