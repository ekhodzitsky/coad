---
schema_version: 1
kind: module_contract
module: validator/report-builders-core
level: subsystem
layer: tooling
purpose: Own core graph, status, proof, schedule, and ledger report builders.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: tools/coad-validator
  context_path: tools/coad-validator
  children: []
  owns_paths:
    - tools/coad-validator/src/coad_validator/graph.py
    - tools/coad-validator/src/coad_validator/graph_report.py
    - tools/coad-validator/src/coad_validator/ledger.py
    - tools/coad-validator/src/coad_validator/proof_artifact_integrity.py
    - tools/coad-validator/src/coad_validator/proof_matrix.py
    - tools/coad-validator/src/coad_validator/schedule.py
    - tools/coad-validator/src/coad_validator/status.py
  context_budget:
    max_files: 13
    max_source_lines: 1750
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
  - name: CoreReportBuilders
    kind: python-api
    visibility: internal
    contract: Builds core machine-readable COAD reports.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests/test_status.py
      command: uv run --locked pytest tests/test_status.py tests/test_graph_report.py tests/test_proof_matrix.py tests/test_schedule.py tests/test_ledger.py
dependencies:
  internal:
    - module: validator/core
      scope: parsed contracts
      reason: Reports consume validation documents and issues.
    - module: schema/report-core
      scope: report payload shape
      reason: Builders must match report schemas.
  external: []
consumers:
  - path: tools/coad-validator/src/coad_validator/report_sources.py
    uses:
      - CoreReportBuilders
invariants: []
verification:
  pre_change:
    - uv run --locked pytest tests/test_status.py tests/test_graph_report.py tests/test_proof_matrix.py tests/test_schedule.py tests/test_ledger.py
  full:
    - uv run --locked pytest
    - coad check .
---

# validator/report-builders-core

Owns core report builder modules.
