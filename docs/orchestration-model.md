# Orchestration Model

COAD separates work into two planes.

## Execution Plane

The execution plane is where agents do work:

- inspect context;
- edit files;
- run checks;
- produce artifacts;
- report handoff output.

## Contract Plane

The contract plane governs work:

- selects relevant module contracts;
- creates task contracts;
- computes dependencies and conflicts;
- builds context packs;
- enforces proof and review gates;
- determines integration readiness.

## Scheduling Rules

An orchestrator may schedule tasks in parallel when:

- dependencies are satisfied;
- write scopes do not overlap;
- module surfaces do not conflict;
- no task writes an invariant another task relies on without ordering;
- required exclusive resources are not already claimed.

`coad-schedule` exports these decisions as machine-readable execution waves.
Tasks in the same wave have satisfied dependencies, fit the goal's
`max_parallel_agents` policy, and do not overlap write scopes. Write-scope
conflicts are reported explicitly so the control plane can serialize rather
than guess.

## Context Pack Rules

A context pack should include:

- task contract;
- relevant module contract frontmatter;
- affected surfaces and invariants;
- known consumers;
- required proof;
- allowed write scope;
- recent relevant failures or known gaps.

It should avoid unrelated files, broad history dumps, and stale conversation summaries.

## Acceptance Rules

The orchestrator accepts work only when:

- proof contract passes;
- review contract passes;
- handoff contract is complete;
- execution ledger entries prove completed task claims;
- contract drift is resolved or accepted;
- integration contract remains satisfiable.
