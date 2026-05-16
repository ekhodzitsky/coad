---
schema_version: 1
kind: review_contract
review_id: <review-id>
target_task: <task-id>
required_reviewers:
  - role: <reviewer-role>
    scope: <review scope>
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

# Review: <review-id>

## Findings

List findings first, ordered by severity.

## Outcome

State pass, blocked, or pass_with_known_gaps.
