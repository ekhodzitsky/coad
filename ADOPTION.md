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

   Keep at least one `MODULE_CONTRACT.md` for the module being changed. Treat
   that module as a workcell: one bounded agent workspace with one active write
   agent. Keep its `README.md` and `TODO.md` current for future agents.
   ````

2. Add one `MODULE_CONTRACT.md`.
3. Add or update the module `README.md` and `TODO.md`.
4. Run `coad check .`.

That is enough to start. Add goal, task, proof, handoff, review, integration,
and ledger contracts only when the workflow needs orchestration beyond module
ownership.

## Adoption Levels

- **Level 0: Agent-ready module context.** `AGENTS.md`, one
  `MODULE_CONTRACT.md`, and module `README.md`/`TODO.md` pass `coad check .`.
- **Level 1: Proven module invariants.** Module surfaces and invariants name
  concrete proof commands.
- **Level 2: Task handoff discipline.** Non-trivial work uses task, proof,
  handoff, review, and integration contracts.
- **Level 3: Ledger-audited orchestration.** Execution ledgers record agent
  work, changed files, and passing proof evidence for completed tasks.

## Phase 1: Identify Boundaries

Pick one or two important ownership boundaries.

Good candidates:

- modules with many consumers;
- modules with fragile invariants;
- modules edited by multiple people or agents;
- modules with public APIs, schemas, protocols, or side effects.

Create module contracts for those boundaries only.

Each boundary should be small enough for a fresh agent to orient in two
minutes. If one boundary needs many unrelated surfaces, many invariants, or a
long README, split it into smaller workcells before adding orchestration.

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

For parallel work, also name the workcell write lease. One leaf workcell should
have at most one active write agent. Composite workcell agents should decompose
and delegate child implementation work instead of editing child code directly.

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
