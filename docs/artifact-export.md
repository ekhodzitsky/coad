# Artifact Export

`coad-export` writes the COAD evidence surface to a deterministic directory that
can be uploaded from CI, attached to a PR, or archived with a release.

It is the file artifact layer above `coad-attest`:

- `coad-attest` binds report digests into one attestation report.
- `coad-export` writes the attestation, every required report, and a manifest to
  disk.

## Usage

```bash
cd tools/coad-validator
uv run --locked coad-export ../.. --schema-dir ../../schema --output-dir /tmp/coad-export
```

The output directory contains:

- `manifest.json` - the export report and artifact index;
- `attestation.json` - the `coad-attest` report;
- one JSON file for each required report, such as `validation-report.json`,
  `ledger-report.json`, and `drift-report.json`.

The CLI also prints the same manifest payload to stdout. The payload is covered
by `schema/reports/export-report.schema.json`.

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

`schema/release-manifest.json` declares `coad-export` as a required release gate,
and `.github/workflows/ci.yml` runs it before drift checking. `coad-drift`
verifies that the CLI, schema, docs, report manifest, release manifest, and CI
gate stay aligned.
