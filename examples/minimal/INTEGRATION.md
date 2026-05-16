---
schema_version: 1
kind: integration_contract
integration_id: checkout-negative-total-integration
baseline: main
policy: local
tasks:
  - checkout-negative-total-guard
merge_order:
  - checkout-negative-total-guard
required_before_integration:
  - task proof contracts pass
  - blocking review findings resolved
  - no checkout contract drift remains
final_verification:
  - command: test checkout
    blocks_readiness: true
  - command: lint checkout
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
---

# Integration: checkout-negative-total-integration

Integration accepts this small graph after task proof, review, drift checks, and
final checkout verification pass.
