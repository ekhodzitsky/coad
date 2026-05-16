---
schema_version: 1
kind: review_contract
review_id: checkout-negative-total-review
target_task: checkout-negative-total-guard
required_reviewers:
  - role: code-reviewer
    scope: correctness and consumer compatibility
  - role: test-engineer
    scope: behavior coverage and regression risk
findings:
  severity_levels:
    - blocker
    - high
    - medium
    - low
acceptance:
  blocks_on:
    - blocker
    - high
  requires_no_unresolved_questions: true
outputs:
  - review_report
  - follow_up_task_contracts
---

# Review: checkout-negative-total-review

The review passes only if the behavior is correct, schema compatibility remains
protected, and no blocking findings are unresolved.
