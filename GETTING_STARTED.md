# Getting Started

COAD adoption should take minutes, not a migration project.

For users, the intended onboarding is one link:

```text
https://github.com/ekhodzitsky/coad
```

Give that link to your coding agent and ask it to adopt COAD in your
repository. The agent should follow `AGENT_ONBOARDING.md`, make the minimal
repository changes, and prove the result with `coad check .`.

You should not need to paste snippets or copy templates by hand.

## Install

Agents can run the validator directly from the COAD repository URL:

```bash
uvx --from 'git+https://github.com/ekhodzitsky/coad.git#subdirectory=tools/coad-validator' coad check .
```

For private repository access over SSH:

```bash
uvx --from 'git+ssh://git@github.com/ekhodzitsky/coad.git#subdirectory=tools/coad-validator' coad check .
```

From this repository:

```bash
cd tools/coad-validator
uv tool install .
```

Or run from a local clone without installing:

```bash
uv run --project tools/coad-validator coad check .
```

## Agent-Led Onboarding

The agent should:

1. Read `AGENT_ONBOARDING.md`.
2. Inspect the target repository.
3. Choose one real module/workcell.
4. Add or update `AGENTS.md` with COAD guidance.
5. Add one `MODULE_CONTRACT.md` for that real workcell.
6. Add or update that workcell's `README.md` and `TODO.md`.
7. Run:

   ```bash
   coad check .
   ```

Expected text output:

```text
coad check: pass
```

For structured output:

```bash
coad check . --format json
```

## Copyable Files

Start from `templates/onboarding/`:

- `AGENTS.md`;
- `MODULE_CONTRACT.md`;
- `module/README.md`;
- `module/TODO.md`.

See `examples/onboarding/` for the smallest complete repository shape that
passes `coad check .`.

## What To Add Later

Start with module ownership. Add heavier contracts only when the workflow needs
them:

- workcell context budgets and write leases for parallel agent work;
- proof on module invariants;
- task and handoff contracts for multi-agent execution;
- review and integration contracts for coordinated delivery;
- execution ledgers for audited orchestration.
