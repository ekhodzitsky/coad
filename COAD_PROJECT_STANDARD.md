# COAD Project Standard

COAD is a methodology for building an agent-navigable codebase.

The goal is not to make agents write more lines per minute. The goal is to make
correct, verified changes cheaper by reducing orientation, hidden coupling,
handoff loss, and review ambiguity.

`coad check .` is only the validator. It tells you whether the repository
follows the standard. The speedup comes from the project shape.

## Target Outcome

An agent should be able to enter a repository and understand the relevant work
context in two minutes:

- what module owns the behavior;
- what surfaces are public or internal;
- what can be changed safely;
- what must not be changed silently;
- which consumers depend on the module;
- which invariants matter;
- which proof commands establish correctness;
- what evidence is needed for handoff.

If an agent must reverse-engineer this by reading the whole repository, the
project is not COAD-native yet.

## Repository Shape

A COAD-native repository has a small global entry and strong local module
contexts.

```text
AGENTS.md
COAD_PROJECT_STANDARD.md
AGENT_FLOW.md
src/
  checkout/
    MODULE_CONTRACT.md
    README.md
    TODO.md
    ...
  billing/
    MODULE_CONTRACT.md
    README.md
    TODO.md
    ...
tests/
docs/
```

Centralized module contracts are allowed when a repository cannot keep contracts
beside code, but each contract must still point to a real module directory with
local `README.md` and `TODO.md`.

## Module As Agent Workspace

Every meaningful module is an agent workspace. An agent assigned to that module
must be able to work from local context first, then inspect implementation
details.

Required local context:

- `MODULE_CONTRACT.md` or a central module contract that points to the module;
- `README.md` explaining purpose, surfaces, consumers, dependencies, and
  invariants;
- `TODO.md` listing current gaps, planned work, and known debt;
- focused tests or proof commands for the module's critical promises.

The module contract is the boundary. The module README is the working map. The
module TODO is the local backlog. Tests and proof commands are the evidence.

## Module Contract Standard

A useful module contract answers these questions without requiring code reading:

- **Purpose:** what the module owns and what it explicitly does not own.
- **Surface:** public/internal functions, types, schemas, commands, events, or
  services other modules rely on.
- **Dependencies:** internal modules and external systems the module depends on,
  with the reason for each dependency.
- **Consumers:** modules, workflows, or users that rely on this module's output.
- **Invariants:** promises that must stay true across changes.
- **Verification:** focused pre-change checks and full verification checks.
- **Agent policy:** allowed mutations, forbidden mutations, and escalation
  triggers.

The best module contract is short enough to read and precise enough to prevent
silent cross-module damage.

## Code Design Rules

COAD-friendly code is shaped for bounded agent work:

- Keep modules cohesive and named after ownership, not implementation detail.
- Put I/O, network calls, filesystem access, subprocesses, and global state at
  edges.
- Keep pure domain logic behind local surfaces that can be tested without
  environment setup.
- Prefer explicit interfaces between modules over reaching into neighbor
  internals.
- Keep public data shapes and events documented as surfaces.
- Keep files small enough that an agent can understand them without dropping
  surrounding context.
- Add tests at the module boundary before changing shared behavior.

Good COAD code lets an agent change internals without reading every consumer.
Bad COAD code requires global archaeology for local edits.

## Change Standard

Every non-trivial change must declare:

- affected module;
- read scope;
- write scope;
- invariants touched or explicitly not touched;
- consumers affected or explicitly not affected;
- proof commands required before handoff;
- contract or local context updates required by the change.

For small one-agent changes, this can live in the agent's working notes or PR
description. For coordinated work, use task, proof, handoff, review, and
integration contracts.

## Multi-Agent Standard

Parallelism is safe only when ownership is explicit.

Agents can work in parallel when:

- their write scopes do not overlap;
- their module contracts do not declare conflicting ownership;
- dependency order is satisfied;
- no agent changes an invariant another active task relies on;
- integration has a clear owner and proof gate.

Agents should not work in parallel merely because files differ. The right unit
of parallelism is module ownership plus proof, not filename coincidence.

## Handoff Standard

An agent never hands off "done" as a claim. A handoff includes:

- changed files;
- affected contracts or module contexts;
- surfaces changed or explicitly unchanged;
- invariants checked;
- proof commands run and results;
- known gaps, risks, and follow-up tasks.

The receiving agent should be able to continue from the handoff without reading
the sender's chat history.

## Adoption Levels

- **Level 0: Agent-ready module context.** `AGENTS.md`, one module contract, and
  module `README.md`/`TODO.md` pass `coad check .`.
- **Level 1: Proven module invariants.** Critical surfaces and invariants have
  concrete proof commands.
- **Level 2: Task handoff discipline.** Coordinated work uses task, proof,
  handoff, review, and integration contracts.
- **Level 3: Ledger-audited orchestration.** Completed agent work is recorded in
  execution ledgers with proof evidence.

Move up only when the workflow needs it. COAD should reduce rework, not create
ceremony.

## Anti-Patterns

- A giant root README that replaces local module context.
- Module contracts that describe aspirations instead of real ownership.
- Consumers listed as "unknown".
- Proof commands that no agent can run.
- Public surfaces changed without updating contracts and consumers.
- TODO files full of stale wishes rather than current work.
- Agents reading the whole repository before reading the relevant module
  contract.
- `coad check .` treated as the source of speed instead of the validator of the
  project shape.
