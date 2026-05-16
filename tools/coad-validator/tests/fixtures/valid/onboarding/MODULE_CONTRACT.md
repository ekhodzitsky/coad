---
schema_version: 1
kind: module_contract
module: checkout
level: root
layer: application
purpose: Keep checkout decisions explicit for agents changing payment-adjacent code.
status: pilot
owners:
  - product-platform
workcell:
  type: leaf
  parent: project
  children: []
  owns_paths:
    - checkout/
  context_budget:
    max_files: 12
    max_source_lines: 1500
    max_contract_lines: 180
    max_readme_lines: 120
    max_todo_lines: 80
authority:
  write_policy: single_active_write_lease
  orchestrator: product-platform
  read_agents: many_allowed
  migration_lease_required:
    - cross-workcell write
    - public surface migration
surface:
  - name: CheckoutService
    kind: service
    visibility: internal
    contract: Converts validated carts into checkout decisions.
    proof:
      kind: unit-test
      target: checkout.checkout_service.creates_checkout_decision
      command: test checkout
dependencies:
  internal: []
  external: []
consumers: []
invariants:
  - id: non-negative-total
    rule: Checkout decisions never contain a negative total.
    proof:
      kind: unit-test
      target: checkout.checkout_service.rejects_negative_total
      command: test checkout
verification:
  pre_change:
    - test checkout
  full:
    - test all
agent_policy:
  allowed_mutations:
    - Change checkout internals while preserving checkout decision semantics.
  forbidden_mutations:
    - Add payment capture side effects to checkout decision code.
  escalation:
    - Public checkout decision schema changes.
---

# checkout

The checkout module owns checkout decisions and the local invariants agents must preserve.
