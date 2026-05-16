# Anti-Patterns

## Documentation Theater

A contract exists, but no proof points to repeatable evidence.

Fix: require proof kind, target, and command, or mark proof as missing debt.

## Contract Sprawl

Every tiny folder gets a contract.

Fix: contract ownership boundaries, not implementation details.

## Vague Consumers

Consumers are listed as "various", "callers", or "unknown".

Fix: list concrete modules, workflows, services, jobs, or user-facing paths.

## Interface Inflation

Agents create interfaces only because contracts mention boundaries.

Fix: add a boundary only when it solves a concrete problem: I/O isolation, multiple real strategies, layer protection, testability, or volatility.

## Proof Laundering

A broad test suite is cited as proof for a specific invariant it does not exercise.

Fix: tie proof to claims and add targeted tests for critical behavior.

## Silent Scope Expansion

A task edits files or surfaces outside its contract.

Fix: block, split into a follow-up task contract, or update orchestration dependencies.

## Stale Contract Acceptance

Work is accepted even though the contract no longer matches code.

Fix: run drift checks or require contract review for changed surfaces and dependencies.

## Chat-Only Handoff

The next worker receives a conversational summary without durable artifacts.

Fix: require handoff contracts with changed files, proof, decisions, gaps, and follow-up tasks.
