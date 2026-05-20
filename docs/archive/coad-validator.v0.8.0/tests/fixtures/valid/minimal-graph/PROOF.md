---
schema_version: 1
kind: proof_contract
proof_id: checkout-negative-total-proof
claim: CheckoutService rejects negative totals and preserves CheckoutDecision schema compatibility.
required:
  - kind: unit-test
    target: checkout.checkout_service.rejects_negative_total
    command: test checkout.checkout_service.rejects_negative_total
    blocks_readiness: true
  - kind: schema
    target: schemas/checkout-decision.schema.json
    command: test schemas/checkout-decision.schema.json
    blocks_readiness: true
accepted_missing: []
artifacts:
  - path: artifacts/test-output/checkout-negative-total.txt
---

# checkout-negative-total-proof

The proof accepts the behavior fix only when both the new negative-total test and
the existing public schema compatibility check pass.
