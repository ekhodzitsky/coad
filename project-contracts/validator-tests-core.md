---
schema_version: 1
kind: module_contract
module: validator/tests-core
level: subsystem
layer: tooling
purpose: Own tests for core validation, path-safety regressions, public check behavior, report schemas, and report versioning.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: tools/coad-validator
  context_path: tools/coad-validator
  children: []
  owns_paths:
    - tools/coad-validator/tests/test_check.py
    - tools/coad-validator/tests/test_report_schemas.py
    - tools/coad-validator/tests/test_report_versioning.py
    - tools/coad-validator/tests/test_validator.py
  context_budget:
    max_files: 12
    max_source_lines: 2800
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
  - name: CoreValidatorTests
    kind: test-suite
    visibility: internal
    contract: Protects core validation and public `coad check` behavior.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests/test_validator.py
      command: uv run --locked pytest tests/test_validator.py tests/test_check.py tests/test_report_schemas.py tests/test_report_versioning.py
dependencies:
  internal:
    - module: validator/core
      scope: tested behavior
      reason: Tests protect core validation.
    - module: validator/check-surface
      scope: tested behavior
      reason: Tests protect public command behavior.
  external: []
consumers:
  - path: .github/workflows/ci.yml
    uses:
      - CoreValidatorTests
invariants: []
verification:
  pre_change:
    - uv run --locked pytest tests/test_validator.py tests/test_check.py
  full:
    - uv run --locked pytest
    - coad check .
---

# validator/tests-core

Owns tests for core validation and check behavior.
