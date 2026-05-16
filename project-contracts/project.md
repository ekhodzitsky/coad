---
schema_version: 1
kind: module_contract
module: project
level: root
layer: methodology
purpose: Own top-level COAD positioning, entrypoints, release metadata, and the project workcell tree.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: project
  context_path: .
  children:
    - contracts
    - docs
    - examples
    - playbooks
    - schema
    - templates
    - tools/coad-validator
  owns_paths:
    - README.md
    - TODO.md
    - AGENTS.md
    - AGENT_ONBOARDING.md
    - AGENT_FLOW.md
    - COAD_PROFILE.json
    - COAD_PROJECT_STANDARD.md
    - CHANGELOG.md
    - GETTING_STARTED.md
    - PRINCIPLES.md
    - VERSION
  context_budget:
    max_files: 12
    max_source_lines: 1500
    max_contract_lines: 180
    max_readme_lines: 260
    max_todo_lines: 80
    max_surfaces: 8
    max_invariants: 8
authority:
  write_policy: root_orchestrator_only
  orchestrator: project
  read_agents: many_allowed
  migration_lease_required:
    - public positioning change
    - release metadata change
    - workcell tree migration
surface:
  - name: COADProjectEntrypoints
    kind: documentation-api
    visibility: public
    contract: Gives humans and agents the canonical top-level entry into COAD.
    proof:
      kind: static-check
      target: README.md AGENT_ONBOARDING.md COAD_PROJECT_STANDARD.md
      command: coad check .
dependencies:
  internal:
    - module: docs
      scope: methodology detail
      reason: Root entrypoints route readers to focused docs.
    - module: tools/coad-validator
      scope: public validator behavior
      reason: Root entrypoints document `coad check .`.
  external: []
consumers:
  - path: https://github.com/ekhodzitsky/coad
    uses:
      - COADProjectEntrypoints
invariants:
  - id: one-link-onboarding
    rule: Public onboarding remains agent-led from the repository URL.
    proof:
      kind: static-check
      target: README.md AGENT_ONBOARDING.md
      command: rg "https://github.com/ekhodzitsky/coad|AGENT_ONBOARDING.md" README.md AGENT_ONBOARDING.md
verification:
  pre_change:
    - coad check .
  full:
    - uv run --locked pytest
    - coad check .
agent_policy:
  allowed_mutations:
    - Clarify top-level positioning while preserving the one-command validator surface.
  forbidden_mutations:
    - Add a second public utility command without changing the methodology contract.
  escalation:
    - Public positioning change
    - Release metadata change
    - Workcell tree migration
---

# project

The project workcell owns COAD's public entrypoints and delegates focused work to child workcells.
