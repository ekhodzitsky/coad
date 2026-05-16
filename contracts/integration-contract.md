# Integration Contract

An Integration Contract defines how accepted task outputs become a coherent delivered change.

It protects the system from accepting individually correct slices that fail when combined.

## Required Fields

```yaml
schema_version: 1
kind: integration_contract
integration_id: billing-tax-release
baseline: main
policy: gated
tasks:
  - billing-tax-rounding
merge_order:
  - billing-tax-rounding
required_before_integration:
  - all task proof contracts pass
  - all blocking review findings resolved
  - no write-scope conflicts remain
final_verification:
  - command: test all
    blocks_readiness: true
  - command: lint all
    blocks_readiness: true
release_evidence:
  required:
    - final_diff
    - final_test_output
    - contract_drift_report
terminal_statuses:
  - ready
  - not_ready
  - blocked
  - failed
```

## Rules

- Integration is not a rubber stamp after agents finish.
- Integration must run proof against the combined result.
- Conflicts should either be resolved through a task contract or reported as blockers.
- Final readiness requires integration proof, not only per-task proof.
- If delivery policy is manual, the integration contract must state the exact human action remaining.
