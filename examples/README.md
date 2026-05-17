# examples

Purpose: provide runnable COAD repository shapes.

Public API:

- `onboarding/` demonstrates the two-minute adoption path.
- `before-after/` demonstrates a failing unstructured repo and the smallest
  passing COAD adoption for the same billing/checkout scenario.
- `minimal/` demonstrates a complete orchestration graph.
- `parallel-work/` demonstrates active leases for coordinated parallel work.

Consumers: README, GETTING_STARTED.md, validator tests, and agents learning COAD.

Invariants: every positive committed example must pass `coad check` from the
repository root. The `before-after/before` half is the only intentionally
failing example and must stay covered by validator tests.
