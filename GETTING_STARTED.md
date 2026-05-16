# Getting Started

COAD adoption should take minutes, not a migration project.

## Install

From this repository:

```bash
cd tools/coad-validator
uv tool install .
```

Or run from a local clone without installing:

```bash
uv run --project tools/coad-validator coad check .
```

## 2-Minute Onboarding

1. Paste this into your repository `AGENTS.md`:

   ````markdown
   Use COAD for agent development coordination.

   Before claiming completion:

   ```bash
   coad check .
   ```

   Keep at least one `MODULE_CONTRACT.md` for the module being changed. The
   module is a workcell: one bounded agent workspace. The module directory must
   include `README.md` and `TODO.md` for future agents.
   ````

2. Add one `MODULE_CONTRACT.md` for a real module.
3. Add that module's `README.md` and `TODO.md`.
4. Run:

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
