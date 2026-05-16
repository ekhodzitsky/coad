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
surface:
  - name: OnboardingExample
    kind: example
    visibility: public
    contract: Shows the smallest repository shape that passes `coad check .`.
    proof:
      kind: smoke
      target: examples/onboarding
      command: coad check examples/onboarding
  - name: MinimalOrchestrationExample
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
      - MinimalOrchestrationExample
invariants:
  - id: examples-stay-runnable
    rule: Every committed example must pass `coad check` from the repository root.
    proof:
      kind: smoke
      target: examples
      command: coad check examples/onboarding && coad check examples/minimal
verification:
  pre_change:
    - coad check examples/onboarding
  full:
    - uv run --locked pytest
    - coad check .
agent_policy:
  allowed_mutations:
    - Add examples that demonstrate real adoption or orchestration flows.
  forbidden_mutations:
    - Add intentionally invalid examples outside tests/fixtures.
  escalation:
    - Example that requires a new contract type
---

# examples

The examples module owns runnable repository shapes used for adoption and tests.
