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

Run it before claiming a task, handoff, review, or PR is complete. A passing
result means the repository's COAD contracts are structurally valid and the
methodology evidence is consistent.

Default text output is intentionally one line:

```text
coad check: pass
```

For automation:

```bash
coad check . --format json
```

The installed validator bundles the COAD schemas. Adopting repositories need
contract files and the command above; they do not need to vendor this repo's
`schema/` directory.

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
`MODULE_CONTRACT.md`, `README.md`, and `TODO.md`.

Before claiming completion, run:

```bash
coad check .
```

Keep at least one `MODULE_CONTRACT.md` for the module being changed. The module
is a workcell: one bounded agent workspace with ownership, surfaces, consumers,
invariants, verification, and write authority. The module directory must include
`README.md` and `TODO.md` so the next agent has local context.

If it fails, fix the contract, module context, proof, handoff, ledger, or policy
issue before claiming the work is complete. Use `coad check . --format json`
when structured output is needed.
````

## Agent-Led Onboarding

1. Read `AGENT_ONBOARDING.md`.
2. Inspect the target repository.
3. Choose one real module/workcell.
4. Add or update `AGENTS.md` with COAD guidance.
5. Add one `MODULE_CONTRACT.md`.
6. Add module `README.md` and `TODO.md`.
7. Run `coad check .`.

## What It Checks

`coad check` verifies the core methodology surface progressively:

- root `AGENTS.md` contains COAD onboarding guidance;
- contract schemas and graph references;
- module contracts resolve to real module directories with `README.md` and
  `TODO.md` agent context files;
- when execution contracts exist, readiness status, proof evidence, scheduling,
  ledger evidence, and goal policy constraints.

It does not do cryptographic provenance, runtime sandboxing, or supply-chain
certification. COAD is a methodology and compliance checker for orchestrated
agent development.
