---
schema_version: 1
kind: module_contract
module: checkout
purpose: Accept cart state and produce checkout decisions for payment and fulfillment.
workcell:
  type: leaf
  owns_paths:
    - checkout/
surface:
  - name: CheckoutDecision
    kind: data
    visibility: public
    contract: Stable read model consumed by payment and fulfillment workflows.
    proof:
      kind: schema
      target: schemas/checkout-decision.schema.json
      command: test schemas/checkout-decision.schema.json
consumers:
  - path: payment
    uses: [CheckoutDecision]
  - path: fulfillment
    uses: [CheckoutDecision]
invariants:
  - id: no-negative-total
    rule: Checkout decisions never contain a negative total.
    proof:
      kind: unit-test
      target: checkout.checkout_service.rejects_negative_total
      command: test checkout.checkout_service.rejects_negative_total
---

# checkout

The checkout module owns application-level checkout decisions. It does not
own pricing rules, payment capture, or fulfillment side effects.

Agents changing checkout should preserve the `CheckoutDecision` schema
unless the task includes consumer migration proof.
