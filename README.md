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

## One Command

The public integration surface is intentionally small:

```bash
coad check .
```

From a local clone:

```bash
cd tools/coad-validator
uv run coad check ../..
```

For another repository, install the tool once and run the same check in that
repository:

```bash
uv tool install /path/to/coad/tools/coad-validator
coad check .
```

The command prints one line and exits non-zero on failure:

```text
coad check: pass
```

Agents that need structured output can use:

```bash
coad check . --format json
```

Everything else in `tools/` is supporting machinery for tests, CI, debugging,
and deeper reports. A normal dev flow should start with `coad check .`.
The validator bundles the COAD schemas, so integrated repositories do not need
to carry a local `schema/` directory just to run the check.

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
tools/       Reference validator and orchestration control-plane tools.
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
8. `docs/agent-integration.md`
9. `docs/release-gates.md`
10. `docs/execution-ledger.md`
11. `docs/conformance-profile.md`
12. `docs/policy-enforcement.md`
13. `docs/attestation-bundle.md`
14. `docs/artifact-export.md`
15. `docs/tool-output-schemas.md`
16. `docs/report-versioning.md`
17. `examples/minimal/`
