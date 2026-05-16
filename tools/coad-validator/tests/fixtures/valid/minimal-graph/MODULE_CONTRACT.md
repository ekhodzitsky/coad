---
schema_version: 1
kind: module_contract
module: checkout
level: root
layer: application
purpose: Accept cart state and produce checkout decisions for payment and fulfillment.
status: pilot
owners:
  - product-platform
workcell:
  type: leaf
  parent: commerce
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
  orchestrator: commerce
  read_agents: many_allowed
  migration_lease_required:
    - cross-workcell write
    - public surface migration
surface:
  - name: CheckoutService
    kind: service
    visibility: internal
    contract: Converts a validated cart into a payment-ready checkout decision.
    proof:
      kind: unit-test
      target: checkout.checkout_service.creates_payment_ready_decision
      command: test checkout.checkout_service.creates_payment_ready_decision
  - name: CheckoutDecision
    kind: data
    visibility: public
    contract: Stable read model consumed by payment and fulfillment workflows.
    proof:
      kind: schema
      target: schemas/checkout-decision.schema.json
      command: test schemas/checkout-decision.schema.json
dependencies:
  internal:
    - module: pricing
      scope: total calculation only
      reason: Checkout must use canonical customer prices.
  external: []
consumers:
  - path: payment
    uses:
      - CheckoutDecision
  - path: fulfillment
    uses:
      - CheckoutDecision
invariants:
  - id: no-negative-total
    rule: Checkout decisions never contain a negative total.
    proof:
      kind: unit-test
      target: checkout.checkout_service.rejects_negative_total
      command: test checkout.checkout_service.rejects_negative_total
verification:
  pre_change:
    - test checkout
  full:
    - test all
    - lint all
agent_policy:
  allowed_mutations:
    - change CheckoutService internals while preserving CheckoutDecision schema
    - add focused tests for checkout invariants
  forbidden_mutations:
    - change CheckoutDecision schema without payment and fulfillment proof
    - bypass pricing module for total calculation
  escalation:
    - public schema change
    - payment workflow behavior change
---

# checkout

The checkout module owns application-level checkout decisions. It does not own pricing rules, payment capture, or fulfillment side effects.

Agents changing checkout should preserve the `CheckoutDecision` schema unless the task explicitly includes consumer migration proof.
