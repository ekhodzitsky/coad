# Execution Ledger

The execution ledger is COAD's durable audit trail for agent work.

Contracts describe what should happen. The schedule says what can happen next.
The ledger records what actually happened and what proof was observed.

## Artifact

An execution ledger is stored as `EXECUTION_LEDGER.json` and validated by
`schema/execution-ledger.schema.json`.

Each ledger names:

- `run_id` - stable identifier for the orchestration run.
- `goal_id` - goal contract this run belongs to.
- `entries` - task execution events.

Each entry records task id, wave, agent id, role, status, timestamps, changed
files, optional handoff path, and proof command results.

Passing proof results must point at durable proof artifacts with declared
`artifact_sha256` and `artifact_bytes`. Text artifacts remain valid when they
are non-empty and digest-bound. JSON artifacts are additionally validated
against `schema/proof-artifact.schema.json`, and their `command` and `status`
must match the ledger proof result they support. The validator also checks that
JSON artifact `exit_code` agrees with `status`, artifact timestamps are ordered
and fit inside the ledger entry window, and `tool`, `cwd`, and `output_path`
stay inside the checked root. A declared `output_path` must exist.

## Completion Rule

A ledger entry with `status: completed` must include a passing proof result for
every proof command required by the referenced task contract. `coad check .`
fails when a completion entry omits required proof.

This prevents a control plane from accepting "done" as a chat claim. Completion
must be backed by durable proof evidence.

## Local Verification

```bash
coad check .
```
