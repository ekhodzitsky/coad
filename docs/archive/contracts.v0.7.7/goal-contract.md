# Goal Contract

A Goal Contract is the root of a COAD contract graph.

It defines the engineering outcome, terminal criteria, orchestration policy,
readiness oracle, budget, risk, and decomposition strategy for a multi-agent
run.

## Required Fields

```yaml
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
  max_parallel_agents: 2
  allow_external_side_effects: false
  require_contract_updates: true
budget:
  time: 4h
  tokens: 200000
  cost: 25.00
readiness_oracle:
  type: proof_contract
  claim: Checkout rejects invalid negative totals without changing public schema.
  required_proof:
    - checkout-negative-total-proof
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
    - checkout-negative-total-proof
  reviews:
    - checkout-negative-total-review
  integration: checkout-negative-total-integration
```

## Semantics

- `objective` describes the requested outcome, not implementation details.
- `goal_class` determines the default proof matrix.
- `terminal_states` lists allowed endings for the run.
- `policy` defines what the orchestrator may do without escalation.
- `budget` constrains time, tokens, cost, compute, or other scarce resources.
- `readiness_oracle` defines how completion is accepted.
- `decomposition` links the goal to task contracts.
- `contracts` names the contract graph members required for readiness.

## Readiness Rule

A goal is `ready` only when:

- every required task contract is complete;
- required proof contracts pass;
- blocking review findings are resolved or explicitly accepted by policy;
- integration contract passes;
- unresolved contract drift is absent or accepted as visible debt;
- the readiness oracle accepts the final state.

## Agent Use

Agents normally do not edit goal contracts unless assigned an orchestration or
planning task. Execution agents use the goal contract to understand the terminal
criteria, policy limits, and proof expectations for their task.

## Anti-Patterns

- Defining a goal without a readiness oracle.
- Treating `not_ready` as failure when it contains useful blocker evidence.
- Letting agents choose terminal criteria after implementation.
- Expanding policy during execution without recording the decision.
