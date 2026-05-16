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

## AGENTS.md Snippet

````markdown
Use COAD for agent development coordination.

Before claiming completion, run:

```bash
coad check .
```

If it fails, fix the contract, proof, handoff, ledger, or policy issue before
claiming the work is complete. Use `coad check . --format json` when structured
output is needed.
````

## What It Checks

`coad check` verifies the core methodology surface:

- contract schemas and graph references;
- module contracts resolve to real module directories with `README.md` and
  `TODO.md` agent context files;
- readiness status;
- proof matrix evidence;
- contract graph exportability;
- task schedule consistency;
- execution ledger evidence;
- goal policy constraints.

It does not do cryptographic provenance, runtime sandboxing, or supply-chain
certification. COAD is a methodology and compliance checker for orchestrated
agent development.
