---
schema_version: 1
kind: module_contract
module: examples/parallel-work-reference
level: subsystem
layer: methodology
purpose: Maintain the public active lease and parallel workcell example.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: examples
  context_path: examples/parallel-work
  children: []
  owns_paths:
    - examples/parallel-work/.coad/leases.yml
    - examples/parallel-work/AGENTS.md
    - examples/parallel-work/MODULE_CONTRACT.md
    - examples/parallel-work/README.md
    - examples/parallel-work/TODO.md
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
  - name: ParallelWorkLeaseExample
    kind: example
    visibility: public
    contract: Shows a composite orchestrator with active leaf write leases.
    proof:
      kind: smoke
      target: examples/parallel-work
      command: coad check examples/parallel-work
dependencies:
  internal:
    - module: contracts
      scope: module contract semantics
      reason: The example instantiates composite and leaf workcell contracts.
    - module: schema/manifests
      scope: lease manifest schema
      reason: The example includes `.coad/leases.yml`.
    - module: tools/coad-validator
      scope: check behavior
      reason: The example must pass the public check command.
  external: []
consumers:
  - path: README.md
    uses:
      - ParallelWorkLeaseExample
  - path: docs/workcells.md
    uses:
      - ParallelWorkLeaseExample
invariants:
  - id: parallel-example-stays-runnable
    rule: The example must pass `coad check examples/parallel-work`.
    proof:
      kind: smoke
      target: examples/parallel-work
      command: coad check examples/parallel-work
verification:
  pre_change:
    - coad check examples/parallel-work
  full:
    - coad check examples/parallel-work
---

# examples/parallel-work-reference

Owns the active lease example for coordinated multi-agent work.
