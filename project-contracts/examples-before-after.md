---
schema_version: 1
kind: module_contract
module: examples/before-after-reference
level: subsystem
layer: methodology
purpose: Maintain the reproducible fail/pass COAD adoption demo.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: examples
  context_path: examples/before-after
  children: []
  owns_paths:
    - examples/before-after/README.md
    - examples/before-after/TODO.md
    - examples/before-after/before/README.md
    - examples/before-after/before/src/billing/discounts.py
    - examples/before-after/before/src/checkout/checkout.py
    - examples/before-after/after/AGENTS.md
    - examples/before-after/after/MODULE_CONTRACT.md
    - examples/before-after/after/src/checkout/checkout.py
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
  - name: BeforeAfterAdoptionDemo
    kind: example
    visibility: public
    contract: Shows a failing unstructured repository beside the smallest passing COAD adoption for the same billing/checkout boundary.
    proof:
      kind: smoke
      target: examples/before-after
      command: uv run --project tools/coad-validator pytest tools/coad-validator/tests/test_check.py -q
dependencies:
  internal:
    - module: tools/coad-validator
      scope: check behavior
      reason: The example exists to demonstrate `coad check` fail/pass behavior.
    - module: schema
      scope: executable validation
      reason: The passing half must remain schema-valid.
  external: []
consumers:
  - path: README.md
    uses:
      - BeforeAfterAdoptionDemo
invariants:
  - id: before-fails-after-passes
    rule: The `before` half fails COAD onboarding and the `after` half passes.
    proof:
      kind: smoke
      target: examples/before-after
      command: uv run --project tools/coad-validator pytest tools/coad-validator/tests/test_check.py -q
verification:
  pre_change:
    - uv run --project tools/coad-validator pytest tools/coad-validator/tests/test_check.py -q
  full:
    - uv run --project tools/coad-validator pytest tools/coad-validator/tests/test_check.py -q
    - coad check .
agent_policy:
  allowed_mutations:
    - Clarify the billing/checkout fail/pass adoption story.
  forbidden_mutations:
    - Make the before half pass without replacing it with another covered failing case.
  escalation:
    - Changing the expected fail/pass behavior
---

# examples/before-after-reference

Owns the reproducible README demo that shows a failing unstructured repository
and the smallest passing COAD adoption for the same billing/checkout boundary.
