---
schema_version: 1
kind: module_contract
module: docs
level: root
layer: methodology
purpose: Explain COAD adoption, positioning, workcell authority, orchestration rules, reports, and operating model.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: project
  children: []
  owns_paths:
    - docs/
  context_budget:
    max_files: 12
    max_source_lines: 1500
    max_contract_lines: 180
    max_readme_lines: 120
    max_todo_lines: 80
authority:
  write_policy: single_active_write_lease
  orchestrator: project
  read_agents: many_allowed
  migration_lease_required:
    - cross-workcell write
    - public surface migration
surface:
  - name: MethodologyDocs
    kind: documentation-api
    visibility: public
    contract: Gives agents and humans the current COAD workflow, positioning, workcell authority model, semantic quality bar, and rationale.
    proof:
      kind: static-check
      target: docs
      command: coad check .
dependencies:
  internal:
    - module: contracts
      scope: contract semantics
      reason: Documentation must describe the canonical methodology.
    - module: schema
      scope: report and contract shape
      reason: Documentation must match executable schemas.
    - module: tools/coad-validator
      scope: public command behavior
      reason: Documentation must match `coad check .`.
  external: []
consumers:
  - path: AGENTS.md
    uses:
      - MethodologyDocs
  - path: README.md
    uses:
      - MethodologyDocs
  - path: AGENT_ONBOARDING.md
    uses:
      - MethodologyDocs
  - path: templates/README.md
    uses:
      - MethodologyDocs
invariants:
  - id: public-command-stays-small
    rule: Public integration docs describe `coad check .` as the only utility command.
    proof:
      kind: static-check
      target: docs
      command: rg "coad-(validate|pack|status|proof|graph|schedule|ledger|profile|policy|attest|export|drift)" README.md ADOPTION.md GETTING_STARTED.md docs tools/README.md tools/coad-validator/README.md
  - id: methodology-stays-repo-native
    rule: Public positioning explains that COAD does not run agents; it makes repositories understandable to agents.
    proof:
      kind: static-check
      target: README.md docs/landscape.md
      command: rg "COAD does not run agents" README.md docs/landscape.md
  - id: workcell-authority-is-core
    rule: Public methodology describes workcells, exclusive write leases, and read-only composite orchestrators.
    proof:
      kind: static-check
      target: README.md COAD_PROJECT_STANDARD.md AGENT_FLOW.md docs/workcells.md
      command: rg "workcell|write lease|Composite" README.md COAD_PROJECT_STANDARD.md AGENT_FLOW.md docs/workcells.md
  - id: onboarding-is-agent-led
    rule: Public onboarding tells users to give agents the COAD repository link rather than manually pasting files.
    proof:
      kind: static-check
      target: README.md GETTING_STARTED.md ADOPTION.md AGENT_ONBOARDING.md docs/agent-integration.md
      command: rg "https://github.com/ekhodzitsky/coad|AGENT_ONBOARDING.md" README.md GETTING_STARTED.md ADOPTION.md AGENT_ONBOARDING.md docs/agent-integration.md
verification:
  pre_change:
    - coad check .
  full:
    - uv run --locked pytest
    - coad check .
agent_policy:
  allowed_mutations:
    - Clarify adoption, operating model, and internal report semantics.
  forbidden_mutations:
    - Reintroduce public `coad-*` command guidance outside internal code/tests.
  escalation:
    - Public adoption flow change
    - New public command
---

# docs

The docs module owns COAD's explanatory surface and adoption guidance.
