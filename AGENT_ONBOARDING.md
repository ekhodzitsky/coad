# Agent Onboarding

You are an agent. A human asked you to adopt COAD in their repository.

## Your task

1. Pick one real module/workcell — public API, fragile invariants, or
   frequent edits.
2. Update target `AGENTS.md` with the snippet below.
3. Add one root `MODULE_CONTRACT.md` (schema below).
4. Ensure the workcell directory has `README.md` + `TODO.md` with one
   line of real content each.
5. Run `coad check .`. Fix what it reports.
6. Hand off: changed files, chosen workcell, validator output, gaps.

Do not add Evidence files (`GOAL_CONTRACT.md`, `TASK_CONTRACT.md`,
`PROOF.md`, `HANDOFF.md`, `REVIEW.md`, `INTEGRATION.md`,
`EXECUTION_LEDGER.json`). They are not in the standard.

## AGENTS.md snippet

```text
Use COAD for agent navigation. https://github.com/ekhodzitsky/coad
Read the relevant MODULE_CONTRACT.md + workcell README.md + TODO.md
before editing. Run `coad check .` before claiming completion.
If .coad/leases.yml exists, declare your write lease. One leaf
workcell, one active write agent.
```

## Minimal MODULE_CONTRACT.md

Required fields: `schema_version`, `kind`, `module`, `purpose`, `workcell`.
Everything else is optional.

```yaml
---
schema_version: 1
kind: module_contract
module: checkout
purpose: Convert validated carts into payment-ready checkout decisions.
workcell:
  type: leaf
  owns_paths:
    - src/checkout/
surface:
  - name: CheckoutDecision
    kind: data
    visibility: public
    contract: Stable read model consumed by payment and fulfillment.
    proof:
      kind: schema
      target: schemas/checkout-decision.schema.json
      command: test schemas/checkout-decision.schema.json
consumers:
  - path: payment
    uses: [CheckoutDecision]
---

# checkout

Application-level checkout decisions. Does not own pricing rules,
payment capture, or fulfillment side effects.
```

## Run the validator

```bash
uvx --from 'git+https://github.com/ekhodzitsky/coad.git#subdirectory=tools/coad-validator' coad check .
```

Expect `coad check: pass`. The validator bundles schemas; do not copy
`schema/` into the target. If `uv` is unavailable, report it as a blocker.

## Done when

`AGENTS.md` mentions `coad check` + COAD URL; root `MODULE_CONTRACT.md`
points at a real `owns_paths` directory that has real `README.md` +
`TODO.md`; `coad check .` prints `pass`.
