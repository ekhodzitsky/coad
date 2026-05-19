# Agent Integration

COAD should be easy to hand to another agent.

The intended user action is:

```text
Give the agent https://github.com/ekhodzitsky/coad and ask it to adopt COAD.
```

The agent should then follow `AGENT_ONBOARDING.md`. The user should not need to
paste snippets, copy templates, or create files manually.

The integration contract is:

```bash
coad check .
```

Agents can run that command directly from the public COAD repository:

```bash
uvx --from 'git+https://github.com/ekhodzitsky/coad.git#subdirectory=tools/coad-validator' coad check .
```

Run it before claiming a task, handoff, review, or PR is complete. A passing
result means the repository's COAD contracts are structurally valid and the
agent evidence trail is internally consistent.

`coad check .` does not execute arbitrary proof commands from module contracts.
Agents must also run the relevant workcell verification commands before
claiming the adopted workcell is ready.

Default text output is intentionally one line:

```text
coad check: pass
```

For automation:

```bash
coad check . --format json
```

The installed validator bundles the COAD schemas. Adopting repositories need
Core files and the command above; they do not need to vendor this repo's
`schema/` directory or write JSON by hand.

For agent-led onboarding, use `AGENT_ONBOARDING.md`. For templates and a
complete minimal example, see `templates/onboarding/` and
`examples/onboarding/`.

## Target AGENTS.md Guidance

Agents adopting COAD should add this guidance to the target repository
`AGENTS.md`, preserving any existing project-specific instructions:

````markdown
Use COAD for agent development coordination.

COAD repository: https://github.com/ekhodzitsky/coad

Before editing, identify the relevant workcell and read its
root `MODULE_CONTRACT.md`, plus the workcell `README.md` and `TODO.md`.

Before claiming completion, run:

```bash
coad check .
```

Keep at least one root `MODULE_CONTRACT.md` for the module being changed. Point
it at the module directory with `workcell.context_path`. The module is a
workcell: one bounded agent workspace with ownership, surfaces, consumers,
invariants, verification, and write authority. The module directory must include
`README.md` and `TODO.md` so the next agent has local context.

If it fails, fix the contract or module context before claiming Core adoption.
For task execution loops, use `coad check . --format json` so agents can follow
typed `next_actions`.
````

## Agent-Led Onboarding

1. Read `AGENT_ONBOARDING.md`.
2. Inspect the target repository.
3. Choose one real module/workcell.
4. Add or update `AGENTS.md` with COAD guidance.
5. Add one root `MODULE_CONTRACT.md`.
6. Set `workcell.context_path` and add module `README.md` and `TODO.md`.
7. Run `coad check .`.

## What It Checks

`coad check` verifies the Core surface first and expands only when Evidence
contracts are present:

- root `AGENTS.md` contains COAD onboarding guidance;
- contract schemas and graph references;
- module contracts resolve to real module directories with `README.md` and
  `TODO.md` agent context files;
- when execution contracts exist, readiness status, proof evidence, scheduling,
  ledger evidence, goal policy constraints, handoff changed-file honesty, and
  task write-scope, proof-result, and contract-update integrity.

It does not do cryptographic provenance, runtime sandboxing, or supply-chain
certification. COAD is a boundary and evidence guardrail for agent-made
changes, not a universal project-management layer.
