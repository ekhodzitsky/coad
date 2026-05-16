---
schema_version: 1
kind: goal_contract
goal_id: <goal-id>
objective: <one sentence engineering outcome>
status: proposed
risk: <low|medium|high|critical>
goal_class: <greenfield|refactor|rewrite|migration|bugfix|audit|performance|documentation|mixed>
terminal_states:
  - ready
  - not_ready
  - blocked_on_human
  - blocked_on_external
  - failed
  - cancelled
policy:
  delivery: <local|draft-pr|auto-pr|manual>
  max_parallel_agents: <integer>
  allow_external_side_effects: false
  require_contract_updates: true
budget:
  time: <duration>
  tokens: <integer>
  cost: <amount>
readiness_oracle:
  type: <proof_contract|manual_acceptance|external_gate>
  claim: <claim that must be accepted for readiness>
  required_proof:
    - <proof-id>
decomposition:
  strategy: <module_boundary|risk_first|dependency_order|manual>
  tasks:
    - <task-id>
contracts:
  modules:
    - <module-id>
  tasks:
    - <task-id>
  proofs:
    - <proof-id>
  reviews:
    - <review-id>
  integration: <integration-id>
---

# <goal-id>

## Intent

Explain the user-visible outcome and constraints.

## Readiness Oracle

Explain what proves the goal is ready.

## Decomposition Notes

Explain why the task split is safe for orchestration.
