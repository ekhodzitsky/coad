# Proof Contract

A Proof Contract defines the evidence required to accept a claim.

Proof must be structured, repeatable when possible, and tied to the risk of the change.

## Proof Kinds

Common proof kinds:

- `unit-test`
- `integration-test`
- `contract-test`
- `golden`
- `schema`
- `static-check`
- `smoke`
- `benchmark`
- `security-scan`
- `review`
- `manual`
- `missing`

## Required Fields

```yaml
schema_version: 1
kind: proof_contract
proof_id: billing-tax-rounding-proof
claim: Tax rounding behavior is correct and deterministic.
required:
  - kind: unit-test
    target: billing.invoice_calculator.tax_rounding
    command: test billing.invoice_calculator.tax_rounding
    blocks_readiness: true
  - kind: regression-test
    target: billing.invoice_calculator.deterministic_totals
    command: test billing.invoice_calculator.deterministic_totals
    blocks_readiness: true
accepted_missing: []
artifacts:
  - path: artifacts/test-output/billing-tax-rounding.txt
```

## Rules

- A proof item must name what it proves.
- A proof command must be runnable unless proof kind is `manual` or `missing`.
- `missing` is visible debt, not success.
- Manual proof must include operator, timestamp, scope, and reason automation is not practical.
- Critical invariants should not accept missing proof without explicit policy.

## Failure Handling

When proof fails, the orchestrator should:

1. Attach the failing artifact to the task.
2. Mark the task `not_ready` or `blocked`.
3. Create a follow-up task contract when the failure is actionable.
4. Refuse readiness until proof passes or policy accepts the gap.
