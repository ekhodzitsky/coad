# templates

Copyable Core starters for a repository adopting COAD.

- `MODULE_CONTRACT.md` — root template for a workcell contract.
- `TODO.md` — root template for a workcell TODO list.
- `onboarding/` — the smallest passing shape: `AGENTS.md`,
  `MODULE_CONTRACT.md`, plus a `module/` directory with `README.md` and
  `TODO.md`.

Templates carry placeholder values. Replace every `<...>` and `TODO`
before committing — `coad check .` will warn on residual placeholders
(`semantic.placeholder`, `semantic.purpose_too_generic`, severity
`warning`/`info`).

See [`AGENT_ONBOARDING.md`](../AGENT_ONBOARDING.md) for the minimal
end-to-end recipe.

Pre-v2 Evidence templates (`GOAL_CONTRACT.md`, `TASK_CONTRACT.md`,
`PROOF.md`, `HANDOFF.md`, `REVIEW.md`, `INTEGRATION.md`) were removed in
v2. Their schemas remain available under `schema/extensions/`; copy from
the schema example sections if a repository needs them.
