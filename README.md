# COAD

[![CI](https://github.com/ekhodzitsky/coad/actions/workflows/ci.yml/badge.svg)](https://github.com/ekhodzitsky/coad/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-%3E%3D3.11-3776AB?logo=python&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-coad%20check%20.-111827)
![Version](https://img.shields.io/badge/version-0.6.0-2563EB)
![Standard](https://img.shields.io/badge/standard-agent--navigable%20codebases-7C3AED)
![Status](https://img.shields.io/badge/status-early%20draft-F59E0B)

**Stop coding agents from editing across invisible boundaries.**

A coding agent can change `src/billing/discounts.ts`, run the obvious tests,
and still break checkout because the real contract lived in someone's head:

- checkout consumes discount totals;
- invoices serialize the same fields;
- analytics depends on old event names;
- only one focused proof command catches the full behavior.

COAD puts that context beside the code before the agent edits. Every important
module gets a small local contract for ownership, surfaces, consumers,
invariants, allowed writes, forbidden mutations, and proof.

COAD does not run agents. COAD makes repositories understandable to agents.

```bash
coad check .
```

## 60-Second Demo

Before COAD, the agent has to infer the boundary from source files and chat:

```text
src/
  checkout/
  billing/
  invoices/
```

The handoff often becomes:

```text
Changed billing. Tests pass.
```

That is not enough information for autonomous edits.

After COAD, the boundary is repo-native:

```text
AGENTS.md
src/
  billing/
    MODULE_CONTRACT.md
    README.md
    TODO.md
```

`MODULE_CONTRACT.md` answers the questions an agent normally has to
reverse-engineer:

- what `billing` owns and does not own;
- which public surfaces checkout, invoices, and analytics consume;
- which invariants must not change silently;
- which files may be edited;
- which proof command must pass before handoff.

Run the reproducible version in [examples/before-after/](examples/before-after/):

```bash
$ uv run --project tools/coad-validator coad check examples/before-after/before --schema-dir schema
coad check: fail

$ uv run --project tools/coad-validator coad check examples/before-after/after --schema-dir schema
coad check: pass
```

The `after/` contract names `BillingTotals`, its checkout consumer, the owned
files, and the proof command. The next agent gets a durable map instead of a
chat summary.

COAD also rejects documentation theater. This fixture has `AGENTS.md`,
`MODULE_CONTRACT.md`, `README.md`, and `TODO.md`, but its public
`BillingTotals` surface names no consumer:

```bash
$ uv run --project tools/coad-validator coad check tools/coad-validator/tests/fixtures/invalid/missing-consumer --schema-dir schema --format json
```

It fails with `semantic.public_surface_without_consumer`. See
[docs/demo-transcripts.md](docs/demo-transcripts.md) for full output.

## Adopt COAD

Give your coding agent this link:

```text
https://github.com/ekhodzitsky/coad
```

Tell it to adopt COAD in your repository. The agent should read
[AGENT_ONBOARDING.md](AGENT_ONBOARDING.md), choose one real workcell, add the
minimal COAD files, run the selected workcell verification commands, run the
validator from the public COAD link, and report the result.

You should not need to paste snippets, copy templates, or create files by hand.

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

The first adoption bar is intentionally small. Add task, proof, handoff,
review, integration, and ledger contracts only when the workflow needs more
orchestration.

From any target repository, an agent can run the validator directly from the
public COAD repository:

```bash
uvx --from 'git+https://github.com/ekhodzitsky/coad.git#subdirectory=tools/coad-validator' coad check .
```

If `coad` is already installed, the command is simply:

```bash
coad check .
```

For structured agent/orchestrator output:

```bash
coad check . --format json
```

See [GETTING_STARTED.md](GETTING_STARTED.md) and
[examples/onboarding/](examples/onboarding/) for the smallest passing setup.
For active write leases and parallel leaf ownership, see
[examples/parallel-work/](examples/parallel-work/).

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
Active write ownership can be declared in `.coad/leases.yml`; `coad check .`
rejects unknown workcells, composite write leases, duplicate write leases, and
write scope outside the workcell's declared ownership.

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
VERSION             Current validator/methodology package version.
CHANGELOG.md        Human-readable release history.
```

## Key Docs

- [COAD_PROJECT_STANDARD.md](COAD_PROJECT_STANDARD.md) - project shape and adoption levels.
- [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) - what an agent should do after receiving the COAD link.
- [AGENT_FLOW.md](AGENT_FLOW.md) - how agents enter, edit, prove, and hand off.
- [docs/demo-transcripts.md](docs/demo-transcripts.md) - reproducible adoption and semantic-quality demo output.
- [docs/adoption-smoke-tests.md](docs/adoption-smoke-tests.md) - real one-link onboarding checks against external repositories.
- [examples/before-after/](examples/before-after/) - reproducible fail/pass adoption demo.
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

Public early draft. The stable integration target is intentionally small:
`coad check .`. The current version is recorded in [VERSION](VERSION), with
release notes in [CHANGELOG.md](CHANGELOG.md).

Keywords: AI agents, agentic development, multi-agent software engineering,
codebase standards, contracts, workcells, orchestration, validation.
