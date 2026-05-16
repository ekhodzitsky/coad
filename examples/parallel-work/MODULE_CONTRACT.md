---
schema_version: 1
kind: module_contract
module: parallel-work
level: root
layer: example
purpose: Demonstrate read-only composite orchestration with independent leaf write leases.
status: pilot
owners:
  - examples-maintainers
workcell:
  type: composite
  context_path: .
  children:
    - parallel-work/api
    - parallel-work/docs
  owns_paths:
    - AGENTS.md
    - MODULE_CONTRACT.md
    - README.md
    - TODO.md
    - .coad/leases.yml
  context_budget:
    max_files: 12
    max_source_lines: 1500
    max_contract_lines: 180
    max_readme_lines: 120
    max_todo_lines: 80
    max_surfaces: 8
    max_invariants: 8
authority:
  write_policy: read_only_orchestrator
  orchestrator: parallel-work
  read_agents: many_allowed
  migration_lease_required:
    - cross-leaf implementation write
surface:
  - name: ParallelWorkExample
    kind: example
    visibility: public
    contract: Shows active leases for one composite orchestrator and two leaf write agents.
    proof:
      kind: smoke
      target: examples/parallel-work
      command: coad check examples/parallel-work
dependencies:
  internal:
    - module: parallel-work/api
      scope: child workcell
      reason: API changes are delegated to the API leaf workcell.
    - module: parallel-work/docs
      scope: child workcell
      reason: Documentation changes are delegated to the docs leaf workcell.
  external: []
consumers:
  - path: README.md
    uses:
      - ParallelWorkExample
invariants:
  - id: composite-does-not-write-child-implementation
    rule: The composite workcell owns only orchestration files and delegates implementation to child workcells.
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
    - Update orchestration guidance and active lease examples.
  forbidden_mutations:
    - Put child implementation files in the composite owns_paths.
  escalation:
    - New child workcell
    - Cross-leaf write scope
---

# parallel-work

Composite workcell for the parallel work lease example.
