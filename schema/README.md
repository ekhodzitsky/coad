# schema

Purpose: define executable JSON schemas for COAD contracts, workcell authority
fields, reports, and manifests.

Public API:

- contract schemas at `schema/*.schema.json`
- proof artifact schema at `schema/proof-artifact.schema.json`
- report schemas at `schema/reports/*.schema.json`
- release, report, and lease manifests

Consumers: `tools/coad-validator`, documentation, examples, and CI.

Invariants: schema files must parse as JSON and remain aligned with contract docs.
