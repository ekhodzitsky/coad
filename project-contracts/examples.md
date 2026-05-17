---
schema_version: 1
kind: module_contract
module: examples
level: root
layer: methodology
purpose: Provide runnable COAD examples for onboarding and full orchestration.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: composite
  parent: project
  children:
    - examples/before-after-reference
    - examples/onboarding-reference
    - examples/minimal-reference
    - examples/parallel-work-reference
  owns_paths:
    - examples/README.md
    - examples/TODO.md
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
  orchestrator: project
  read_agents: many_allowed
  migration_lease_required:
    - cross-workcell write
    - public surface migration
surface:
  - name: OnboardingExample
    kind: example
    visibility: public
    contract: Shows the smallest repository shape that passes `coad check .`.
    proof:
      kind: smoke
      target: examples/onboarding
      command: coad check examples/onboarding
  - name: BeforeAfterAdoptionDemo
    kind: example
    visibility: public
    contract: Shows a failing unstructured repository beside the smallest passing COAD adoption for the same module boundary.
    proof:
      kind: smoke
      target: examples/before-after
      command: uv run --project tools/coad-validator pytest tools/coad-validator/tests/test_check.py -q
  - name: MinimalOrchestrationExample
    kind: example
    visibility: public
    contract: Shows a complete goal/task/proof/handoff/review/integration graph.
    proof:
      kind: smoke
      target: examples/minimal
      command: coad check examples/minimal
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
      scope: contract examples
      reason: Examples instantiate the canonical contract types.
    - module: schema
      scope: executable validation
      reason: Examples must satisfy JSON schemas.
    - module: tools/coad-validator
      scope: check behavior
      reason: Examples must pass the public check command.
  external: []
consumers:
  - path: GETTING_STARTED.md
    uses:
      - OnboardingExample
  - path: README.md
    uses:
      - BeforeAfterAdoptionDemo
      - MinimalOrchestrationExample
      - ParallelWorkLeaseExample
invariants:
  - id: examples-stay-runnable
    rule: Every positive committed example must pass `coad check` from the repository root; the before half of the before/after demo is intentionally failing and test-covered.
    proof:
      kind: smoke
      target: examples
      command: coad check examples/onboarding && coad check examples/minimal && coad check examples/parallel-work && coad check examples/before-after/after && uv run --project tools/coad-validator pytest tools/coad-validator/tests/test_check.py -q
verification:
  pre_change:
    - coad check examples/onboarding
  full:
    - uv run --locked pytest
    - coad check .
agent_policy:
  allowed_mutations:
    - Add examples that demonstrate real adoption or orchestration flows.
    - Add documented before/after demos when the failing half is covered by validator tests.
  forbidden_mutations:
    - Add intentionally invalid examples outside tests/fixtures or documented before/after demos.
  escalation:
    - Example that requires a new contract type
---

# examples

The examples module owns runnable repository shapes used for adoption and tests.
