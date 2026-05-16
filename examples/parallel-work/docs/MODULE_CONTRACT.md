---
schema_version: 1
kind: module_contract
module: parallel-work/docs
level: subsystem
layer: example
purpose: Demonstrate a leaf workcell with one active write lease for documentation work.
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
  - name: ExampleDocsSurface
    kind: documentation
    visibility: internal
    contract: Placeholder docs surface owned by the docs leaf workcell.
    proof:
      kind: smoke
      target: examples/parallel-work
      command: coad check examples/parallel-work
dependencies:
  internal:
    - module: parallel-work/api
      scope: documented surface
      reason: Docs describe the API leaf's placeholder surface.
  external: []
consumers:
  - path: README.md
    uses:
      - ExampleDocsSurface
invariants:
  - id: docs-work-stays-in-docs-leaf
    rule: Documentation changes stay inside the docs leaf ownership.
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
    - Change files under docs/.
  forbidden_mutations:
    - Change api/ files under the docs write lease.
  escalation:
    - Shared API/docs surface change
---

# parallel-work/docs

Leaf workcell for docs-side example changes.
