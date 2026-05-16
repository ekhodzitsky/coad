---
schema_version: 1
kind: module_contract
module: playbooks
level: root
layer: methodology
purpose: Capture repeatable agent orchestration workflows.
status: pilot
owners:
  - methodology-maintainers
surface:
  - name: OrchestrationPlaybooks
    kind: documentation-api
    visibility: public
    contract: Describes repeatable flows for multi-agent COAD execution.
    proof:
      kind: static-check
      target: playbooks
      command: coad check .
dependencies:
  internal:
    - module: contracts
      scope: workflow gates
      reason: Playbooks must use canonical contract semantics.
    - module: docs
      scope: operating model
      reason: Playbooks must align with documented orchestration rules.
  external: []
consumers:
  - path: docs/orchestration-model.md
    uses:
      - OrchestrationPlaybooks
invariants:
  - id: playbooks-do-not-bypass-proof
    rule: Playbooks must not accept agent completion without proof or visible debt.
    proof:
      kind: review
      target: playbooks
      command: coad check .
verification:
  pre_change:
    - coad check .
  full:
    - uv run --locked pytest
    - coad check .
agent_policy:
  allowed_mutations:
    - Add or refine orchestration flows that preserve COAD proof gates.
  forbidden_mutations:
    - Add workflows that accept prose-only completion claims.
  escalation:
    - Workflow that changes acceptance or review policy
---

# playbooks

The playbooks module owns repeatable orchestration flows.
