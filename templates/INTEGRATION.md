---
schema_version: 1
kind: integration_contract
integration_id: <integration-id>
baseline: <branch-or-release-baseline>
policy: <local|draft-pr|auto-pr|manual|gated>
tasks: []
merge_order: []
required_before_integration:
  - all task proof contracts pass
  - all blocking review findings resolved
  - no write-scope conflicts remain
final_verification: []
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

# Integration: <integration-id>

## Plan

Describe integration order, conflict handling, and final proof.

## Terminal Status

State final readiness and evidence.
