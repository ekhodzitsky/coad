# Handoff Contract

A Handoff Contract defines the minimum durable output of an agent or reviewer.

It exists so the next agent does not depend on chat context or vague summaries.

## Required Fields

```yaml
schema_version: 1
kind: handoff_contract
task_id: billing-tax-rounding
status: complete
changed_files:
  - billing/invoice_calculator.py
  - billing/test_invoice_calculator.py
proof_results:
  - command: test billing.invoice_calculator.tax_rounding
    status: pass
contract_updates:
  - path: billing/MODULE_CONTRACT.md
    reason: Added tax rounding invariant proof.
decisions:
  - id: tax-rounding-location
    decision: Round once at invoice total level.
    reason: Prevents accumulated line-item rounding error.
known_gaps: []
follow_up_tasks: []
```

## Status Values

- `complete`
- `not_ready`
- `blocked_on_human`
- `blocked_on_external`
- `failed_infra`
- `cancelled`

## Rules

- Handoff must include evidence paths or command summaries.
- Handoff must list known gaps, even if the list is empty.
- Handoff must identify contract changes or state that none were needed.
- A blocker must include exact recovery action.
- Follow-up work should be proposed as task contracts, not prose wishes.
