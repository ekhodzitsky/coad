# COAD: Contract-Orchestrated Agent Development

Contract-Orchestrated Agent Development (COAD) is a methodology for orchestrated agentic software development.

It turns modules, tasks, proofs, handoffs, reviews, and integrations into machine-readable contracts so multiple agents can work on one system without relying on chat memory, guesses, or vague "looks done" claims.

## Core Idea

A software system can be changed safely by agents when every unit of work is bounded by explicit contracts:

```text
Goal
  -> Task Contracts
    -> Module Contracts
    -> Proof Contracts
    -> Handoff Contracts
    -> Review Contracts
  -> Integration Contract
```

Agents do not own completion claims. Contracts and proof do.

## Why This Exists

Agentic coding breaks down when agents:

- read too much irrelevant context;
- miss hidden consumers and invariants;
- work in overlapping write scopes;
- hand off with summaries instead of evidence;
- accept completion without repeatable verification;
- create abstractions because the real boundaries are invisible.

COAD makes boundaries, permissions, proof, and readiness explicit enough for an orchestrator to route work and for agents to execute it safely.

## Contract Types

- **Goal Contract**: why the work exists, how readiness is decided, and what policy constrains orchestration.
- **Module Contract**: what a module owns, exposes, depends on, and promises.
- **Task Contract**: what one agent or worker must change, prove, and avoid.
- **Proof Contract**: what evidence is required before a claim can be accepted.
- **Handoff Contract**: what must be passed from one worker to the next.
- **Review Contract**: what review gates block acceptance.
- **Integration Contract**: when accepted slices can be combined and delivered.

## Minimal Lifecycle

1. Define the goal and terminal criteria.
2. Decompose the goal into task contracts.
3. Bind each task to module contracts and write scopes.
4. Dispatch agents with bounded context packs.
5. Require proof contracts before completion.
6. Convert review findings into new task contracts.
7. Integrate only after review, proof, and dependency gates pass.
8. Update contracts when surfaces, dependencies, invariants, or verification change.

## Repository Map

```text
contracts/   Canonical contract type definitions.
templates/   Copyable contract templates.
schema/      Machine-readable contract and tool-output schemas.
docs/        Methodology details: proof matrix, maturity, rules, anti-patterns.
playbooks/   Repeatable orchestration flows.
examples/    Small reference examples.
tools/       Reference validator and context pack generator.
```

## Status

Private draft. The goal is to turn the original Module Contract Pattern into a broader methodology for contract-driven orchestration of multi-agent software work.

## Recommended Reading Order

1. `SPEC.md`
2. `PRINCIPLES.md`
3. `contracts/goal-contract.md`
4. `docs/contract-graph.md`
5. `docs/proof-matrix.md`
6. `docs/context-packs.md`
7. `docs/validator.md`
8. `docs/release-gates.md`
9. `docs/execution-ledger.md`
10. `docs/conformance-profile.md`
11. `docs/tool-output-schemas.md`
12. `docs/report-versioning.md`
13. `examples/minimal/`
