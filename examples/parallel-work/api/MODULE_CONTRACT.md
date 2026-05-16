---
schema_version: 1
kind: module_contract
module: parallel-work/api
level: subsystem
layer: example
purpose: Demonstrate a leaf workcell with one active write lease for API work.
status: pilot
owners:
  - examples-maintainers
workcell:
  type: leaf
  parent: parallel-work
  context_path: .
  children: []
  owns_paths:
    - .
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
  orchestrator: parallel-work
  read_agents: many_allowed
surface:
  - name: ExampleApiSurface
    kind: module
    visibility: internal
    contract: Placeholder API surface owned by the API leaf workcell.
    proof:
      kind: smoke
      target: examples/parallel-work
      command: coad check examples/parallel-work
dependencies:
  internal: []
  external: []
consumers:
  - path: docs/README.md
    uses:
      - ExampleApiSurface
invariants:
  - id: api-work-stays-in-api-leaf
    rule: API implementation changes stay inside the API leaf ownership.
    proof:
      kind: static-check
      target: .coad/leases.yml
      command: coad check examples/parallel-work
verification:
  pre_change:
    - coad check examples/parallel-work
  full:
    - coad check examples/parallel-work
agent_policy:
  allowed_mutations:
    - Change files under api/.
  forbidden_mutations:
    - Change docs/ files under the API write lease.
  escalation:
    - Shared API/docs surface change
---

# parallel-work/api

Leaf workcell for API-side example changes.
