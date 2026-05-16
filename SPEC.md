# COAD Specification

Contract-Orchestrated Agent Development (COAD) is a methodology for coordinating multiple software agents through explicit contracts and proof.

## Product Thesis

A large software change should not be assigned to an agent as an open-ended instruction. It should be decomposed into bounded contracts that define ownership, context, permissions, proof, review, and integration.

The central promise:

> Multiple agents can work safely in parallel when their work is governed by contracts that are machine-readable, proof-backed, and enforced by an orchestrator.

## Scope

COAD applies to:

- multi-agent software development;
- large refactors and migrations;
- bugfix campaigns;
- security or reliability hardening;
- long-running autonomous engineering goals;
- teams that mix humans and agents.

COAD does not require a specific language, framework, agent runtime, repository layout, or issue tracker.

## Non-Goals

- Replace human product judgment.
- Create contracts for every tiny implementation detail.
- Treat diagrams or prose as proof by themselves.
- Encourage speculative interfaces or abstractions.
- Let agents weaken invariants without explicit acceptance.
- Let orchestration hide uncertainty behind success claims.

## Contract Graph

A COAD run is described by a contract graph:

```text
Goal Contract
  -> Task Contracts
    -> Module Contracts
    -> Proof Contracts
    -> Review Contracts
    -> Handoff Contracts
  -> Integration Contract
```

The graph answers:

- what must change;
- who or what owns each change;
- which modules and surfaces are involved;
- which changes can run in parallel;
- which evidence is required;
- which reviews block acceptance;
- what must be integrated before final readiness.

## Contract Types

### Module Contract

Defines an ownership boundary. It describes purpose, surface, dependencies, consumers, invariants, and verification.

### Task Contract

Defines one bounded unit of work. It binds a goal slice to owner, read scope, write scope, dependencies, allowed mutations, forbidden mutations, proof, and handoff.

### Proof Contract

Defines evidence required for acceptance. It should be structured and repeatable.

### Handoff Contract

Defines what a worker must report or produce when its task exits, whether it succeeds, blocks, or fails.

### Review Contract

Defines review gates and how findings become follow-up task contracts.

### Integration Contract

Defines how accepted work is combined, verified, released, or blocked.

## Orchestration Lifecycle

1. **Intake**: capture the goal, constraints, budget, risk, and terminal criteria.
2. **Classification**: classify the change type: greenfield, refactor, rewrite, migration, bugfix, audit, performance, documentation, or mixed.
3. **Contract discovery**: identify relevant module contracts and missing contract debt.
4. **Decomposition**: create task contracts with dependencies and scopes.
5. **Scheduling**: select tasks that can run without contract or write-scope conflicts.
6. **Context packing**: build bounded context packs from contracts and source artifacts.
7. **Execution**: dispatch agents under task contracts.
8. **Proof collection**: collect test results, static checks, artifacts, diffs, and review outputs.
9. **Review**: run required review contracts and convert blocking findings into new task contracts.
10. **Integration**: combine accepted tasks in dependency order and run final proof.
11. **Contract update**: update changed contracts and record missing proof debt.
12. **Terminal status**: report ready, not_ready, blocked, failed, cancelled, or needs_more_budget with evidence.

## Agent Decision Loop

For each task, an agent should:

1. Read the task contract.
2. Read relevant module contract frontmatter.
3. Inspect only the context needed to preserve the contract.
4. Confirm allowed and forbidden mutations.
5. Make the smallest change that satisfies the task.
6. Add or update proof for changed behavior, surface, dependency, or invariant.
7. Run required verification or record why it could not run.
8. Update contracts when drift is introduced or resolved.
9. Produce handoff output with changed files, proof, risks, blockers, and follow-up work.

## Completion Rule

A task is complete only when:

- requested behavior is implemented or explicitly blocked;
- affected contracts are preserved or updated;
- required proof contracts pass or missing proof is explicitly accepted by policy;
- required review contracts pass or known gaps are accepted;
- handoff output is complete;
- no unresolved contract drift remains.

A goal is complete only when all required task contracts are complete and the integration contract has passed.

## Drift Rule

Contract drift exists when:

- code exposes a surface not listed in a module contract;
- a listed surface no longer exists;
- a dependency is used but not declared;
- a consumer is known but not listed;
- an invariant is violated or lacks proof;
- a proof command no longer runs;
- verification requirements no longer match the module's risk.

Drift should block readiness unless explicitly accepted as debt.

## Maturity

COAD adoption should be incremental. A project can start with module contracts and proof matrices, then add task contracts, drift checks, context pack generation, and integration gates.

The methodology is successful when it reduces unsafe parallelism, vague handoffs, stale docs, missing tests, and unsupported completion claims.
