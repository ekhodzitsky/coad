---
schema_version: 1
kind: module_contract
module: validator/tests-reports
level: subsystem
layer: tooling
purpose: Own tests for report builders, cached report composition, report CLIs, exports, profiles, and packs.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: tools/coad-validator
  context_path: tools/coad-validator
  children: []
  owns_paths:
    - tools/coad-validator/tests/test_attest.py
    - tools/coad-validator/tests/test_drift.py
    - tools/coad-validator/tests/test_export.py
    - tools/coad-validator/tests/test_graph_index.py
    - tools/coad-validator/tests/test_graph_report.py
    - tools/coad-validator/tests/test_ledger.py
    - tools/coad-validator/tests/test_pack.py
    - tools/coad-validator/tests/test_policy.py
    - tools/coad-validator/tests/test_profile.py
    - tools/coad-validator/tests/test_proof_matrix.py
    - tools/coad-validator/tests/test_schedule.py
    - tools/coad-validator/tests/test_status.py
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
  - name: ReportBuilderTests
    kind: test-suite
    visibility: internal
    contract: Protects report builders and internal report CLI behavior.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests
      command: uv run --locked pytest tests/test_attest.py tests/test_export.py tests/test_profile.py tests/test_drift.py tests/test_policy.py
dependencies:
  internal:
    - module: validator/report-builders-core
      scope: tested behavior
      reason: Tests protect core report builders.
    - module: validator/report-builders-governance
      scope: tested behavior
      reason: Tests protect governance report builders.
  external: []
consumers:
  - path: .github/workflows/ci.yml
    uses:
      - ReportBuilderTests
invariants: []
verification:
  pre_change:
    - uv run --locked pytest tests/test_attest.py tests/test_export.py tests/test_profile.py
  full:
    - uv run --locked pytest
    - coad check .
---

# validator/tests-reports

Owns tests for report builders and internal report CLIs.
