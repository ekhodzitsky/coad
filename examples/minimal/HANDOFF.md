---
schema_version: 1
kind: handoff_contract
task_id: checkout-negative-total-guard
status: complete
changed_files:
  - EXECUTION_LEDGER.json
  - TASK_CONTRACT.md
proof_results:
  - command: test checkout.checkout_service.rejects_negative_total
    status: pass
  - command: test schemas/checkout-decision.schema.json
    status: pass
contract_updates:
  - path: checkout/MODULE_CONTRACT.md
    reason: Added proof for the no-negative-total invariant.
  - path: TASK_CONTRACT.md
    reason: Allowed durable proof artifact output for ledger-backed verification.
decisions:
  - id: reject-negative-total-at-checkout-boundary
    decision: Reject invalid totals in CheckoutService before producing CheckoutDecision.
    reason: Keeps payment and fulfillment consumers from handling impossible totals.
known_gaps: []
follow_up_tasks: []
---

# Handoff: checkout-negative-total-guard

This example handoff shows the durable output a worker should leave behind for
review and integration.
