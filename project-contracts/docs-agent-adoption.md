---
schema_version: 1
kind: module_contract
module: docs/agent-adoption
level: subsystem
layer: methodology
purpose: Explain how agents adopt COAD, make decisions, receive context, and avoid common anti-patterns.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: docs
  context_path: docs
  children: []
  owns_paths:
    - docs/agent-decision-rules.md
    - docs/agent-integration.md
    - docs/adoption-smoke-tests.md
    - docs/anti-patterns.md
    - docs/context-packs.md
    - docs/demo-transcripts.md
    - docs/landscape.md
    - docs/maturity-model.md
    - docs/normative-language.md
    - docs/orchestration-model.md
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
  orchestrator: docs
  read_agents: many_allowed
surface:
  - name: AgentAdoptionDocs
    kind: documentation-api
    visibility: public
    contract: Gives agents the operating rules for adopting and using COAD in a target repository.
    proof:
      kind: static-check
      target: docs/agent-integration.md
      command: coad check .
dependencies:
  internal:
    - module: docs/workcell-model
      scope: workcell terminology
      reason: Adoption docs rely on workcell authority and budget semantics.
  external: []
consumers:
  - path: AGENT_ONBOARDING.md
    uses:
      - AgentAdoptionDocs
  - path: README.md
    uses:
      - AgentAdoptionDocs
invariants: []
verification:
  pre_change:
    - coad check .
  full:
    - coad check .
---

# docs/agent-adoption

Owns public guidance for agents adopting COAD and operating inside COAD projects.
