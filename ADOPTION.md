# Adoption Guide

COAD adoption should be incremental. The goal is safer orchestration, not a
documentation migration project.

## Agent Quickstart

Give an agent this repository link and one rule:

```bash
coad check .
```

The command is the default integration point. It should be run before a handoff,
review, or PR claim. It prints a single result line for humans and supports
`--format json` for orchestration.

The installed tool bundles the COAD schemas, so a repository can adopt the
methodology with contract files and `coad check .` without copying this repo's
`schema/` directory.

If `coad check .` fails, fix the contracts, proof, handoff, ledger, or policy
issue it reports before claiming the work is complete.

## 2-Minute Onboarding

1. Paste this into the repository `AGENTS.md`:

   ````markdown
   Use COAD for agent development coordination.

   Before claiming completion:

   ```bash
   coad check .
   ```

   Keep at least one `MODULE_CONTRACT.md` for the module being changed, and
   keep that module's `README.md` and `TODO.md` current for future agents.
   ````

2. Add one `MODULE_CONTRACT.md`.
3. Add or update the module `README.md` and `TODO.md`.
4. Run `coad check .`.

That is enough to start. Add goal, task, proof, handoff, review, integration,
and ledger contracts only when the workflow needs orchestration beyond module
ownership.

## Phase 1: Identify Boundaries

Pick one or two important ownership boundaries.

Good candidates:

- modules with many consumers;
- modules with fragile invariants;
- modules edited by multiple people or agents;
- modules with public APIs, schemas, protocols, or side effects.

Create module contracts for those boundaries only.

For each contracted module, keep a real module directory with:

- `README.md` for agent-facing ownership, API, dependencies, and invariants;
- `TODO.md` for current gaps and planned work.

Add module-local `AGENTS.md` only when that module needs rules beyond the
repository default.

## Phase 2: Add Proof

For each contracted module:

- list key surfaces;
- list invariants;
- attach proof to each critical promise;
- mark missing proof explicitly.

Do not block adoption on perfect proof coverage.

## Phase 3: Use Task Contracts

For the next non-trivial change, write a task contract before execution.

The task contract should define:

- owner role;
- read scope;
- write scope;
- change class;
- acceptance criteria;
- required proof;
- handoff requirements.

## Phase 4: Add Review And Integration Contracts

Use review contracts when work affects public surface, security, performance,
compatibility, or multiple modules.

Use integration contracts when multiple task outputs must be combined.

## Phase 5: Check Drift

Start with manual drift review:

- did the surface change?
- did dependencies change?
- did consumers change?
- did invariants change?
- did proof commands change?

Later, automate drift checks with schema validation, import analysis, and proof
command checks.

## Recommended First Week

1. Contract one high-value module.
2. Add proof matrix for its most common change classes.
3. Run one real task through a task contract.
4. Capture handoff output.
5. Review what felt useful and what felt ceremonial.

The best first implementation is small enough that people keep using it.
