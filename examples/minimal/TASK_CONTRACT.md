---
schema_version: 1
kind: task_contract
task_id: checkout-negative-total-guard
objective: Prevent checkout decisions with negative totals.
owner_role: executor
status: pending
risk: medium
change_class: behavior_change
modules:
  - checkout
read_scope:
  - checkout/**
  - pricing/**
write_scope:
  - checkout/**
dependencies: []
allowed_mutations:
  - update CheckoutService validation
  - add checkout tests
forbidden_mutations:
  - change CheckoutDecision schema
  - change pricing rules
acceptance:
  - CheckoutService rejects negative totals before producing CheckoutDecision.
  - Existing payment and fulfillment consumers remain compatible.
proof:
  required:
    - kind: unit-test
      target: checkout.checkout_service.rejects_negative_total
      command: test checkout.checkout_service.rejects_negative_total
    - kind: schema
      target: schemas/checkout-decision.schema.json
      command: test schemas/checkout-decision.schema.json
handoff:
  required_fields:
    - changed_files
    - proof_results
    - contract_updates
    - known_gaps
---

# checkout-negative-total-guard

This task is safe for one executor agent. It touches checkout validation only and must not change pricing or public checkout schema.
