---
schema_version: 1
kind: module_contract
module: onboarding-checkout
level: root
layer: application
purpose: Keep checkout decisions explicit for agents changing payment-adjacent code.
status: pilot
owners:
  - product-platform
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

# onboarding-checkout

The onboarding checkout module owns checkout decisions and the local invariants
agents must preserve.
