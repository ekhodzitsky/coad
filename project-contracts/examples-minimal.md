---
schema_version: 1
kind: module_contract
module: examples/minimal-reference
level: subsystem
layer: methodology
purpose: Maintain the compact full-contract graph example.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: examples
  context_path: examples/minimal
  children: []
  owns_paths:
    - examples/minimal/AGENTS.md
    - examples/minimal/EXECUTION_LEDGER.json
    - examples/minimal/GOAL_CONTRACT.md
    - examples/minimal/HANDOFF.md
    - examples/minimal/INTEGRATION.md
    - examples/minimal/MODULE_CONTRACT.md
    - examples/minimal/PROOF.md
    - examples/minimal/README.md
    - examples/minimal/REVIEW.md
    - examples/minimal/TASK_CONTRACT.md
    - examples/minimal/TODO.md
    - examples/minimal/artifacts/schema-test.txt
    - examples/minimal/artifacts/unit-test.txt
  context_budget:
    max_files: 14
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
  - name: MinimalGraphExample
    kind: example
    visibility: public
    contract: Shows a complete goal/task/proof/handoff/review/integration graph.
    proof:
      kind: smoke
      target: examples/minimal
      command: coad check examples/minimal
dependencies:
  internal:
    - module: contracts
      scope: complete contract graph
      reason: The example instantiates every orchestration contract type.
    - module: schema
      scope: executable validation
      reason: The example must remain schema-valid.
  external: []
consumers:
  - path: README.md
    uses:
      - MinimalGraphExample
invariants: []
verification:
  pre_change:
    - coad check examples/minimal
  full:
    - coad check examples/minimal
---

# examples/minimal-reference

Owns the compact end-to-end COAD graph example.
