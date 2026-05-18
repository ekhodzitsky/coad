# Attestation Bundle

The internal attestation report builds a hashable evidence bundle from the
required COAD control-plane reports.

The bundle does not replace the individual reports. It binds them together with
SHA-256 digests so an orchestrator, reviewer, or CI system can refer to one
stable acceptance artifact.

Use the internal artifact export report when the same evidence must be written
to disk as PR or release artifacts. See `docs/artifact-export.md`.

## Included Reports

The current bundle includes:

- agent guidance report;
- validation report;
- status report;
- proof matrix;
- graph report;
- schedule report;
- ledger report;
- profile report;
- policy report;
- handoff integrity report;
- task scope integrity report;
- proof result integrity report;
- contract update integrity report;
- drift report.

Every included report is required. If any required report has `ok: false`, the
attestation fails and records the failing report name.

## Digest Contract

Each report is canonicalized as sorted JSON and hashed with SHA-256. The bundle
digest is the SHA-256 hash of the ordered report name/digest/ok/required set.

This makes the bundle deterministic for the same inputs and sensitive to report
content changes.

The public verification path remains `coad check .`.
