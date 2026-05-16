---
schema_version: 1
kind: module_contract
module: validator/report-builders-governance
level: subsystem
layer: tooling
purpose: Own governance, export, profile, policy, drift, attestation, and pack report builders.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: tools/coad-validator
  context_path: tools/coad-validator
  children: []
  owns_paths:
    - tools/coad-validator/src/coad_validator/artifact_export.py
    - tools/coad-validator/src/coad_validator/attest.py
    - tools/coad-validator/src/coad_validator/drift.py
    - tools/coad-validator/src/coad_validator/graph_index.py
    - tools/coad-validator/src/coad_validator/pack.py
    - tools/coad-validator/src/coad_validator/policy.py
    - tools/coad-validator/src/coad_validator/profile.py
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
  - name: GovernanceReportBuilders
    kind: python-api
    visibility: internal
    contract: Builds governance and export reports used by higher conformance levels.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests/test_profile.py
      command: uv run --locked pytest tests/test_profile.py tests/test_policy.py tests/test_attest.py tests/test_export.py tests/test_drift.py tests/test_pack.py
dependencies:
  internal:
    - module: validator/report-builders-core
      scope: report dependencies
      reason: Governance reports compose core report evidence.
    - module: schema/report-aux
      scope: report payload shape
      reason: Builders must match auxiliary schemas.
  external: []
consumers:
  - path: tools/coad-validator/src/coad_validator/report_sources.py
    uses:
      - GovernanceReportBuilders
invariants: []
verification:
  pre_change:
    - uv run --locked pytest tests/test_profile.py tests/test_policy.py tests/test_attest.py tests/test_export.py tests/test_drift.py tests/test_pack.py
  full:
    - uv run --locked pytest
    - coad check .
---

# validator/report-builders-governance

Owns governance and export report builders.
