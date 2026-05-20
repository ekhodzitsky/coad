---
schema_version: 1
kind: goal_contract
goal_id: checkout-negative-total-hardening
objective: Prevent checkout decisions with invalid negative totals.
status: proposed
risk: medium
goal_class: bugfix
terminal_states:
  - ready
  - not_ready
  - blocked_on_human
  - blocked_on_external
  - failed
  - cancelled
policy:
  delivery: local
  max_parallel_agents: 1
  allow_external_side_effects: false
  require_contract_updates: true
budget:
  time: 4h
  tokens: 200000
  cost: 25.00
readiness_oracle:
  type: proof_contract
  claim: Checkout rejects negative totals without changing the public checkout decision schema.
  required_proof:
    - missing-proof-contract
decomposition:
  strategy: module_boundary
  tasks:
    - checkout-negative-total-guard
contracts:
  modules:
    - checkout
  tasks:
    - checkout-negative-total-guard
  proofs:
    - missing-proof-contract
  reviews:
    - checkout-negative-total-review
  integration: checkout-negative-total-integration
---

# checkout-negative-total-hardening

This goal is intentionally small. It demonstrates how COAD binds a user-visible
bugfix to one task, one module boundary, proof, review, and integration.
