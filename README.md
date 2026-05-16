# COAD

[![CI](https://github.com/ekhodzitsky/coad/actions/workflows/ci.yml/badge.svg)](https://github.com/ekhodzitsky/coad/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-%3E%3D3.11-3776AB?logo=python&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-coad%20check%20.-111827)
![Standard](https://img.shields.io/badge/standard-agent--navigable%20codebases-7C3AED)
![Status](https://img.shields.io/badge/status-early%20draft-F59E0B)

**The agent-navigable codebase standard.**

Make repositories legible to coding agents: small workcells, explicit write
authority, proof-backed handoffs, and one validator.

Give your agent this repository link; the agent should do the onboarding.

```bash
coad check .
```

COAD is not an agent runtime, IDE plugin, prompt pack, or project management
framework. It is a repository standard for shaping codebases so agents can
orient quickly, edit inside clear boundaries, and prove their work.

Contract-Orchestrated Agent Development (COAD) is the methodology behind that
standard.

## Positioning

COAD makes a codebase understandable to agents before they start editing.

It gives every important part of a project a small local contract:

- what it owns;
- what it exposes;
- who depends on it;
- what must stay true;
- who may write;
- which proof is required before work can be called done.

Use COAD when you want agents to work from durable repo context instead of chat
memory, whole-repository dumps, and vague "looks done" claims.

## Why COAD

Agentic development breaks down when agents:

- read too much irrelevant context;
- miss hidden consumers and invariants;
- edit overlapping scopes in parallel;
- hand off chat summaries instead of evidence;
- claim completion without repeatable proof;
- invent abstractions because real boundaries are invisible.

COAD turns those hidden assumptions into repo-native contracts and validates
the result with one command.

## Core Model

A COAD-native project is a tree of **workcells**.

A workcell is the smallest independently ownable, documentable, and verifiable
unit of agent work. It may be a package, module, service, feature area, or docs
area.

```text
Project Workcell
  -> Composite Workcell
    -> Leaf Workcell
```

Leaf workcells are the normal implementation unit. Each leaf workcell has at
most one active write agent. Composite workcells are read-only orchestration
units: they decompose work, assign write leases, collect proof, and delegate
implementation to child workcells.

`MODULE_CONTRACT.md` is the compatibility filename for a workcell contract.

## What You Add

Start with one real module:

```text
AGENTS.md
src/
  checkout/
    MODULE_CONTRACT.md
    README.md
    TODO.md
```

The module contract defines:

- ownership boundary;
- public and internal surfaces;
- dependencies and consumers;
- invariants;
- verification commands;
- allowed and forbidden mutations;
- workcell authority and write policy.

Keep local docs short. If a module README becomes an encyclopedia, the workcell
is probably too large and should be split.

## One Command

Install from a local clone:

```bash
cd tools/coad-validator
uv tool install .
```

Run the public check:

```bash
coad check .
```

Expected output:

```text
coad check: pass
```

For structured agent/orchestrator output:

```bash
coad check . --format json
```

From this repository without installing:

```bash
cd tools/coad-validator
uv run coad check ../..
```

## One-Link Onboarding

Give your coding agent this link:

```text
https://github.com/ekhodzitsky/coad
```

Tell it to adopt COAD in your repository. The agent should read
[AGENT_ONBOARDING.md](AGENT_ONBOARDING.md), choose one real workcell, add the
minimal COAD files, run `coad check .`, and report the result.

You should not need to paste snippets, copy templates, or create files by hand.
If the agent cannot install/run the validator because of network, package, or
repository-access limits, that is a tooling blocker for the agent to report.

The first adoption bar is intentionally small. Add task, proof, handoff,
review, integration, and ledger contracts only when the workflow needs more
orchestration.

See [GETTING_STARTED.md](GETTING_STARTED.md) and
[examples/onboarding/](examples/onboarding/) for the smallest passing setup.

## Repository Map

```text
contracts/          Human-readable contract semantics.
templates/          Copyable starter contracts.
schema/             JSON schemas for contracts and reports.
docs/               Methodology details and operating rules.
playbooks/          Repeatable orchestration flows.
examples/           Reference COAD project shapes.
project-contracts/  COAD contracts for this repository itself.
tools/              Reference validator. Public command: coad check .
```

## Key Docs

- [COAD_PROJECT_STANDARD.md](COAD_PROJECT_STANDARD.md) - project shape and adoption levels.
- [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) - what an agent should do after receiving the COAD link.
- [AGENT_FLOW.md](AGENT_FLOW.md) - how agents enter, edit, prove, and hand off.
- [docs/workcells.md](docs/workcells.md) - workcell tree, context budgets, write leases, and authority.
- [docs/module-contract-checklist.md](docs/module-contract-checklist.md) - semantic quality checklist for module contracts.
- [docs/landscape.md](docs/landscape.md) - comparison with adjacent agent-development projects.
- [docs/validator.md](docs/validator.md) - validator behavior and report semantics.

## Landscape

COAD sits beside agent runtimes and spec-first workflow systems. It is lighter
by design: a repository standard plus one public command.

Adjacent projects worth knowing:

- [GitHub Spec Kit](https://github.com/github/spec-kit)
- [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)
- [Superpowers](https://github.com/obra/superpowers)
- [GSD / Get Shit Done](https://github.com/gsd-build/get-shit-done)
- [Agent OS](https://github.com/buildermethods/agent-os)
- [Repomix](https://github.com/yamadashy/repomix)
- [OpenHands](https://github.com/OpenHands/OpenHands)
- [Cline](https://github.com/cline/cline)
- [Roo Code](https://github.com/RooCodeInc/Roo-Code)
- [Aider](https://github.com/Aider-AI/aider)

Those projects mostly define agent workflows, agent runtimes, or context
packaging. COAD defines how the repository itself exposes boundaries,
ownership, proof, and safe write scope to any agent.

## Status

Early draft. The stable public integration target is intentionally small:
`coad check .`.

Keywords: AI agents, agentic development, multi-agent software engineering,
codebase standards, contracts, workcells, orchestration, validation.
