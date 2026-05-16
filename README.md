# COAD: Contract-Orchestrated Agent Development

Contract-Orchestrated Agent Development (COAD) is a methodology for orchestrated agentic software development.

It turns modules, tasks, proofs, handoffs, reviews, and integrations into machine-readable contracts so multiple agents can work on one system without relying on chat memory, guesses, or vague "looks done" claims.

## Core Idea

A COAD-native codebase is an agent-navigable codebase: every important module
has enough local context for an agent to understand ownership, surfaces,
consumers, invariants, proof, and safe write scope before reading the whole
repository.

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

## 2-Minute Onboarding

1. Paste the COAD snippet into the repository `AGENTS.md`.
2. Add one `MODULE_CONTRACT.md` for a real module.
3. Give that module a `README.md` and `TODO.md`.
4. Run `coad check .`.

That is the first adoption bar. Repositories with only module contracts get a
light structural check. When goal/task/proof/handoff contracts are added,
`coad check .` automatically includes the orchestration evidence checks.

Use `GETTING_STARTED.md` for the copy-paste flow and `examples/onboarding/` for
the smallest complete passing example.

Use `COAD_PROJECT_STANDARD.md` for the project shape and `AGENT_FLOW.md` for the
agent work protocol.

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
project-contracts/
             COAD module contracts for this repository's real modules.
tools/       Reference validator. Public command: `coad check .`.
```

## Status

Private draft. The goal is to turn the original Module Contract Pattern into a broader methodology for contract-driven orchestration of multi-agent software work.

## Recommended Reading Order

1. `SPEC.md`
2. `GETTING_STARTED.md`
3. `COAD_PROJECT_STANDARD.md`
4. `AGENT_FLOW.md`
5. `PRINCIPLES.md`
6. `contracts/goal-contract.md`
7. `docs/contract-graph.md`
8. `docs/proof-matrix.md`
9. `docs/context-packs.md`
10. `docs/validator.md`
11. `docs/agent-integration.md`
12. `docs/release-gates.md`
13. `docs/execution-ledger.md`
14. `docs/conformance-profile.md`
15. `docs/policy-enforcement.md`
16. `docs/attestation-bundle.md`
17. `docs/artifact-export.md`
18. `docs/tool-output-schemas.md`
19. `docs/report-versioning.md`
20. `examples/minimal/`
