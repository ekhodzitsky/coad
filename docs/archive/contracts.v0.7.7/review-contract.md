# Review Contract

A Review Contract defines gates that can block acceptance.

Review is not a final opinion paragraph. It is a structured check with findings that either pass, block, or create follow-up task contracts.

## Required Fields

```yaml
schema_version: 1
kind: review_contract
review_id: billing-tax-rounding-review
target_task: billing-tax-rounding
required_reviewers:
  - role: code-reviewer
    scope: correctness and regressions
  - role: test-engineer
    scope: coverage and flake risk
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
```

## Review Types

- architecture review
- code review
- test review
- security review
- performance review
- migration compatibility review
- anti-slop cleanup review

## Rules

- Findings must reference concrete behavior, contract, or artifact.
- Blocking findings become task contracts.
- Style-only comments should not block unless they violate a documented contract.
- Review passes only when blocking findings are fixed, rejected by policy, or accepted as known gaps.
