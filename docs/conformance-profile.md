# Conformance Profile

`COAD_PROFILE.json` declares the methodology level this repository claims to
support. `coad-profile` verifies that claim with concrete tool evidence.

## Current Level

The current profile is `ledger_audited_orchestration`.

This means the repository has:

- validated contract schemas and graph references;
- schedulable task waves;
- execution ledgers audited against task proof contracts;
- release gates and drift checks wired into CI.

## Checks

Each profile check has an `id`, tool, requirement flag, and description. Required
checks must pass for the repository to be conformant.

Current required checks:

- `contracts-valid` via `coad-validate`;
- `schedule-builds` via `coad-schedule`;
- `execution-ledger-verified` via `coad-ledger`;
- `release-gates-clean` via `coad-drift`.

## Local Verification

```bash
cd tools/coad-validator
uv run --locked coad-profile ../.. --schema-dir ../../schema
```
