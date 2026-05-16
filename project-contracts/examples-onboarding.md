---
schema_version: 1
kind: module_contract
module: examples/onboarding-reference
level: subsystem
layer: methodology
purpose: Maintain the smallest public COAD onboarding example.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: examples
  context_path: examples/onboarding
  children: []
  owns_paths:
    - examples/onboarding/
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
  - name: OnboardingReferenceExample
    kind: example
    visibility: public
    contract: Shows the minimum repository shape that can pass `coad check .`.
    proof:
      kind: smoke
      target: examples/onboarding
      command: coad check examples/onboarding
dependencies:
  internal:
    - module: templates
      scope: onboarding shape
      reason: The example should stay aligned with starter templates.
  external: []
consumers:
  - path: AGENT_ONBOARDING.md
    uses:
      - OnboardingReferenceExample
invariants: []
verification:
  pre_change:
    - coad check examples/onboarding
  full:
    - coad check examples/onboarding
---

# examples/onboarding-reference

Owns the smallest public adoption example.
