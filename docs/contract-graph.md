# Contract Graph

The contract graph is the durable orchestration model for COAD.

It links the goal, task slices, modules, proof, reviews, handoffs, and
integration into one inspectable structure.

## Graph Shape

```text
Goal Contract
  -> Task Contracts
    -> Module Contracts
    -> Proof Contracts
    -> Review Contracts
    -> Handoff Contracts
  -> Integration Contract
```

## Nodes

| Node | Purpose |
| --- | --- |
| Goal Contract | Defines objective, policy, budget, terminal states, and readiness oracle. |
| Task Contract | Defines one bounded unit of work for an agent or human. |
| Module Contract | Defines ownership boundary, surface, dependencies, consumers, invariants, and verification. |
| Proof Contract | Defines evidence required to accept a claim. |
| Handoff Contract | Defines durable output from a worker. |
| Review Contract | Defines review gates and blocking findings. |
| Integration Contract | Defines how accepted task outputs become final delivered work. |

## Edges

Edges are dependencies, not decoration.

- A goal **owns** task contracts.
- A task **touches** module contracts.
- A task **requires** proof contracts.
- A task **emits** handoff contracts.
- A task **is blocked by** review contracts.
- Integration **depends on** accepted task contracts and their proof.

## Parallel Scheduling

Two task contracts MAY run in parallel only when all of these are true:

- their dependencies are complete;
- their write scopes do not overlap;
- neither task writes a module surface the other reads without dependency order;
- neither task weakens an invariant the other relies on;
- required exclusive reviewers, environments, or external resources are free;
- the goal policy allows the required concurrency.

The orchestrator MUST serialize tasks when write scopes, public surfaces,
invariants, or external side effects conflict.

## Conflict Types

| Conflict | Meaning | Default action |
| --- | --- | --- |
| write/write | Two tasks write the same path, surface, or contract field. | Serialize. |
| read/write | One task reads a surface another task changes. | Add dependency. |
| invariant | A task changes an invariant another task assumes. | Escalate or serialize. |
| proof | Two tasks rely on incompatible proof requirements. | Split or escalate. |
| integration | Accepted slices cannot be combined cleanly. | Create integration fix task. |

## Drift Handling

When code changes invalidate a contract edge, the graph is stale.

The orchestrator MUST either:

- update the affected contract;
- create a task contract for the update;
- record accepted drift as visible missing proof or known debt;
- block readiness.

## Terminal Rule

The graph reaches `ready` only when every required path from goal to integration
has passing proof or explicitly accepted debt.

## Machine Report

When execution contracts are present, `coad check . --format json` includes a
graph check. The internal graph report includes contract nodes and typed edges
such as `goal_has_task`,
`task_requires_proof`, `handoff_for_task`, and `integration_orders_task`.
Nodes carry a unique `key` in `<kind>:<id>` form so graph consumers can
distinguish contracts that intentionally share the same domain id, such as a
task contract and its handoff contract.

The output is covered by `schema/reports/graph-report.schema.json`.
