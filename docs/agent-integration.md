# Agent Integration

COAD should be easy to hand to another agent.

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

For a copy-paste start, use `GETTING_STARTED.md` and
`templates/onboarding/`. For a complete minimal example, see
`examples/onboarding/`.

## AGENTS.md Snippet

````markdown
Use COAD for agent development coordination.

Before claiming completion, run:

```bash
coad check .
```

Keep at least one `MODULE_CONTRACT.md` for the module being changed. The module
directory must include `README.md` and `TODO.md` so the next agent has local
context.

If it fails, fix the contract, module context, proof, handoff, ledger, or policy
issue before claiming the work is complete. Use `coad check . --format json`
when structured output is needed.
````

## 2-Minute Onboarding

1. Paste the snippet above into `AGENTS.md`.
2. Add one `MODULE_CONTRACT.md`.
3. Add module `README.md` and `TODO.md`.
4. Run `coad check .`.

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
