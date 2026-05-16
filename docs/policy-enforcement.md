# Policy Enforcement

COAD goal contracts carry orchestration policy. `coad-policy` turns selected
policy fields into executable checks so agents cannot silently weaken the run
contract.

## Current Checks

`allow_external_side_effects: false` means task contracts must not declare
`external_side_effects`.

`require_contract_updates: true` means each task contract's handoff requirements
must include `contract_updates`.

These checks are intentionally small and direct. They cover high-risk
orchestration failures without pretending to be a complete authorization system.

## Task Side Effects

When a task needs external side effects, declare them explicitly:

```yaml
external_side_effects:
  - kind: network
    target: https://api.example.invalid/deploy
    reason: trigger deployment
```

The goal policy must allow external side effects before such a task can pass
policy enforcement.

## Local Verification

```bash
cd tools/coad-validator
uv run --locked coad-policy ../.. --schema-dir ../../schema
```
