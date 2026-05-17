---
schema_version: 1
kind: module_contract
module: billing
level: root
layer: application
purpose: Own discount total calculation used by checkout presentation.
status: pilot
owners:
  - product-platform
workcell:
  type: leaf
  context_path: src/billing
  children: []
  owns_paths:
    - src/billing/
  context_budget:
    max_files: 12
    max_source_lines: 1500
    max_contract_lines: 180
    max_readme_lines: 120
    max_todo_lines: 80
    max_surfaces: 8
    max_invariants: 8
authority:
  write_policy: single_active_write_lease
  orchestrator: product-platform
  read_agents: many_allowed
  migration_lease_required:
    - public billing total shape change
surface:
  - name: BillingTotals
    kind: data-shape
    visibility: public
    contract: Provides discount totals consumed by checkout summary construction.
    proof:
      kind: unit-test
      target: billing.discounts.discount_total
      command: python -m pytest tests/test_billing.py
dependencies:
  internal: []
  external: []
consumers:
  - path: src/checkout/checkout.py
    uses:
      - BillingTotals
invariants:
  - id: non-negative-discount
    rule: Discount totals must never make checkout totals negative.
    proof:
      kind: unit-test
      target: billing.discounts.discount_total
      command: python -m pytest tests/test_billing.py
verification:
  pre_change:
    - python -m pytest tests/test_billing.py
  full:
    - python -m pytest
agent_policy:
  allowed_mutations:
    - Change discount calculation internals while preserving BillingTotals.
  forbidden_mutations:
    - Rename `discount_cents` without updating checkout consumers.
  escalation:
    - Billing total shape changes
---

# billing

The billing workcell owns discount totals. Checkout consumes the public
`BillingTotals` shape.
