---
schema_version: 1
kind: module_contract
module: examples/invalid-reference
level: subsystem
layer: methodology
purpose: Maintain public intentionally failing examples used by README and docs.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: examples
  context_path: examples/invalid
  children: []
  owns_paths:
    - examples/invalid/README.md
    - examples/invalid/TODO.md
    - examples/invalid/missing-consumer/AGENTS.md
    - examples/invalid/missing-consumer/MODULE_CONTRACT.md
    - examples/invalid/missing-consumer/billing/README.md
    - examples/invalid/missing-consumer/billing/TODO.md
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
  orchestrator: examples
  read_agents: many_allowed
surface:
  - name: InvalidSemanticQualityExample
    kind: example
    visibility: public
    contract: Shows a public `BillingTotals` surface failing because no consumer is declared.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests/test_validator.py
      command: uv run --locked pytest tests/test_validator.py
dependencies:
  internal:
    - module: tools/coad-validator
      scope: check behavior
      reason: The example exists to demonstrate semantic-quality validation.
  external: []
consumers:
  - path: README.md
    uses:
      - InvalidSemanticQualityExample
invariants:
  - id: invalid-example-fails-directly
    rule: Checking examples/invalid/missing-consumer directly must fail with semantic.public_surface_without_consumer.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests/test_validator.py
      command: uv run --locked pytest tests/test_validator.py
verification:
  pre_change:
    - uv run --locked pytest tests/test_validator.py
  full:
    - uv run --locked pytest
    - coad check .
---

# examples/invalid-reference

Owns public intentionally failing examples.
