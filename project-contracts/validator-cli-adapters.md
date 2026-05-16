---
schema_version: 1
kind: module_contract
module: validator/cli-adapters
level: subsystem
layer: tooling
purpose: Own thin module-specific CLI adapters for internal report commands.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: tools/coad-validator
  context_path: tools/coad-validator
  children: []
  owns_paths:
    - tools/coad-validator/src/coad_validator/attest_cli.py
    - tools/coad-validator/src/coad_validator/drift_cli.py
    - tools/coad-validator/src/coad_validator/export_cli.py
    - tools/coad-validator/src/coad_validator/graph_report_cli.py
    - tools/coad-validator/src/coad_validator/ledger_cli.py
    - tools/coad-validator/src/coad_validator/pack_cli.py
    - tools/coad-validator/src/coad_validator/policy_cli.py
    - tools/coad-validator/src/coad_validator/profile_cli.py
    - tools/coad-validator/src/coad_validator/proof_matrix_cli.py
    - tools/coad-validator/src/coad_validator/schedule_cli.py
    - tools/coad-validator/src/coad_validator/status_cli.py
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
  - name: InternalReportCLIs
    kind: cli
    visibility: internal
    contract: Exposes report builders for tests and internal artifact generation without adding public workflow commands.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests
      command: uv run --locked pytest
dependencies:
  internal:
    - module: validator/report-builders-core
      scope: report builders
      reason: CLI adapters call report builders.
    - module: validator/report-builders-governance
      scope: report builders
      reason: CLI adapters call report builders.
  external: []
consumers:
  - path: tools/coad-validator/tests
    uses:
      - InternalReportCLIs
invariants: []
verification:
  pre_change:
    - uv run --locked pytest tests/test_attest.py tests/test_export.py tests/test_profile.py
  full:
    - uv run --locked pytest
    - coad check .
---

# validator/cli-adapters

Owns thin adapters for internal report commands.
