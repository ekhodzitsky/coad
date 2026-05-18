# invalid examples

Purpose: provide intentionally failing COAD examples for documentation and
demo transcripts.

Public API:

- `missing-consumer/` demonstrates semantic-quality failure for public surfaces
  without declared consumers.

Consumers: README, docs/demo-transcripts.md, and validator tests.

Invariants: invalid examples must fail for the documented reason when checked
directly, and must be skipped during repository-wide validation.
