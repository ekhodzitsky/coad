# Minimal Example

This example shows the smallest useful COAD contract graph:

- one goal contract for the orchestration root;
- one module contract for `checkout`;
- one task contract for a behavior fix;
- proof tied to tests and schema compatibility;
- a handoff artifact shape;
- a review gate;
- an integration contract;
- explicit forbidden mutations that prevent scope drift.

The files are illustrative and do not require an actual checkout implementation.
