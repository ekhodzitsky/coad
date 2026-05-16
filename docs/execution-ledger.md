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
