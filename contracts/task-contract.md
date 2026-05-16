# Task Contract

A Task Contract describes one bounded unit of agent work.

It is the orchestration unit used to schedule, parallelize, review, and accept changes.

## Required Fields

```yaml
schema_version: 1
kind: task_contract
task_id: billing-tax-rounding
objective: Fix tax rounding for invoice totals.
owner_role: executor
status: pending
risk: medium
change_class: behavior_change
modules:
  - billing
read_scope:
  - billing/**
  - pricing/**
write_scope:
  - billing/**
dependencies: []
allowed_mutations:
  - update invoice total calculation
  - add or update billing tests
forbidden_mutations:
  - change public InvoiceSummary schema
  - add external dependencies
acceptance:
  - Tax is rounded once at invoice total level.
  - Existing deterministic total invariant remains true.
proof:
  required:
    - proof_id: billing-tax-rounding-proof
      kind: unit-test
      target: billing.invoice_calculator.tax_rounding
      command: test billing.invoice_calculator.tax_rounding
    - proof_id: billing-tax-rounding-proof
      kind: regression-test
      target: billing.invoice_calculator.deterministic_totals
      command: test billing.invoice_calculator.deterministic_totals
handoff:
  required_fields:
    - changed_files
    - proof_results
    - contract_updates
    - known_gaps
```

## Scheduling Rule

Two task contracts may run in parallel only when:

- their write scopes do not overlap;
- one task does not write a module surface another task reads without dependency ordering;
- their module contracts do not require the same exclusive review or integration lock;
- their dependencies are complete.

## Completion Rule

A task is complete only when:

- acceptance criteria are met;
- proof requirements pass or are explicitly accepted as missing proof debt;
- affected module contracts are updated if needed;
- handoff output is complete;
- no forbidden mutation occurred.

## Agent Use

The task contract is the agent's operating brief. The agent should not silently widen scope. If the task cannot be completed inside the contract, the agent should return a blocker or propose a follow-up task contract.
