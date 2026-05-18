# Artifact Export

The internal artifact export report writes the COAD evidence surface to a
deterministic directory that can be uploaded from CI, attached to a PR, or
archived with a release.

It is the file artifact layer above the internal attestation report:

- the attestation report binds report digests into one report;
- the export report writes the attestation, every required report, and a
  manifest to disk.

The output directory contains:

- `manifest.json` - the export report and artifact index;
- `attestation.json` - the attestation report;
- one JSON file for each required report, such as `agent-guidance.json`,
  `validation-report.json`, `handoff-integrity.json`,
  `task-scope-integrity.json`, `proof-result-integrity.json`,
  `contract-update-integrity.json`, `ledger-report.json`, and
  `drift-report.json`.

The payload is covered by `schema/reports/export-report.schema.json`.

## Contract

The manifest includes:

- `schema_version: 1`;
- `ok` and `status`;
- `bundle_digest` for the exported artifact set;
- `attestation_bundle_digest` copied from the attestation report;
- `artifact_count`;
- per-artifact `name`, `producer`, `path`, `required`, `ok`, `status`,
  `digest`, and `bytes`;
- structured `issues`.

Required report failures make the export fail with `status: export_failed`.
The bundle is still written so reviewers can inspect the failed evidence instead
of losing the diagnostic artifact.

## Release Gate

Artifact export is an internal evidence surface. It is not part of the public
CLI; the public repository check remains `coad check .`.
