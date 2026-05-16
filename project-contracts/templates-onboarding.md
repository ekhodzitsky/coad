---
schema_version: 1
kind: module_contract
module: templates/onboarding
level: subsystem
layer: methodology
purpose: Maintain the minimal starter template set for two-minute onboarding.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: templates
  context_path: templates
  children: []
  owns_paths:
    - templates/onboarding/
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
  orchestrator: templates
  read_agents: many_allowed
surface:
  - name: OnboardingTemplates
    kind: template-set
    visibility: public
    contract: Gives agents the smallest COAD files needed to start adoption.
    proof:
      kind: static-check
      target: templates/onboarding
      command: coad check .
dependencies:
  internal:
    - module: docs/agent-adoption
      scope: onboarding flow
      reason: Starter templates must match one-link onboarding guidance.
  external: []
consumers:
  - path: AGENT_ONBOARDING.md
    uses:
      - OnboardingTemplates
invariants: []
verification:
  pre_change:
    - coad check .
  full:
    - coad check .
---

# templates/onboarding

Owns minimal starter files for COAD adoption.
