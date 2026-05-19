# COAD

[![CI](https://github.com/ekhodzitsky/coad/actions/workflows/ci.yml/badge.svg)](https://github.com/ekhodzitsky/coad/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-%3E%3D3.11-3776AB?logo=python&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-coad%20check%20.-111827)
![Status](https://img.shields.io/badge/status-early%20draft-F59E0B)

## What COAD is

COAD is a small standard for making repositories agent-navigable. A coding
agent that enters a COAD-conforming repository can find an ownership
boundary, read local context, and understand which files are safe to edit —
without reverse-engineering the project from chat history.

The standard fits in fifteen rules. See [STANDARD.md](STANDARD.md). One
command checks them:

```bash
coad check .
```

## Why

A coding agent can change `src/billing/discounts.ts`, run the obvious tests,
and still break checkout because the real contract lived in someone's head:
checkout consumes discount totals, invoices serialize the same fields, only
one focused proof command catches the full behavior. COAD puts that context
beside the code, in `MODULE_CONTRACT.md` next to the module, so the next
agent (or human) does not have to rediscover it.

COAD does not run agents. It is not a methodology, an orchestration runtime,
or a workflow. It is a repository shape plus a checker for that shape.

## Demo

Before COAD, the agent has to infer the boundary from source files:

```text
src/
  checkout/
  billing/
```

After COAD:

```text
AGENTS.md
MODULE_CONTRACT.md
src/
  billing/
    README.md
    TODO.md
```

The `MODULE_CONTRACT.md` names what `billing` owns, its public surfaces,
its consumers, its invariants, and a proof command. Run the reproducible
fail-then-pass demo in [examples/before-after/](examples/before-after/):

```bash
$ uv run --project tools/coad-validator coad check examples/before-after/before --schema-dir schema
coad check: fail

$ uv run --project tools/coad-validator coad check examples/before-after/after --schema-dir schema
coad check: pass
```

## Adopt COAD

Give your coding agent this link and ask it to adopt COAD in your
repository:

```text
https://github.com/ekhodzitsky/coad
```

The agent should read [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md), choose one
real workcell, add the four minimal files, and run `coad check .`. You
should not need to paste snippets or copy templates by hand.

Or run the validator yourself from any target repository:

```bash
uvx --from 'git+https://github.com/ekhodzitsky/coad.git#subdirectory=tools/coad-validator' coad check .
```

The validator bundles the COAD schemas. Python 3.11 or newer and `uv` are
required.

## What you add

```text
AGENTS.md
MODULE_CONTRACT.md
src/
  <workcell>/
    README.md
    TODO.md
```

The root `MODULE_CONTRACT.md` points at the workcell directory with
`workcell.context_path` and lists owned paths under that boundary. See
[examples/minimal/](examples/minimal/) for the smallest passing shape.

## Repository map

```text
STANDARD.md              The fifteen-rule standard. Source of truth.
AGENT_ONBOARDING.md      One-page instruction for an agent adopting COAD.
schema/                  module-contract.schema.json + lease-manifest.schema.json.
schema/extensions/       Evidence-layer contract schemas (optional).
schema/reports/          JSON schemas for validator report output.
examples/                Reference COAD project shapes.
docs/                    Validator behavior, landscape, demo transcripts.
docs/archive/            Pre-v2 prose (methodology, principles, agent flow).
tools/coad-validator/    Reference validator. Public command: coad check .
project-contracts/       COAD contracts for this repository itself.
VERSION                  Validator/standard version.
CHANGELOG.md             Release history.
```

## Core vs Evidence

COAD ships with two layers:

- **Core (the standard).** COAD-001..COAD-015 in `STANDARD.md`. Every
  conforming repository must pass these.
- **Evidence (optional, off by default).** Task/proof/handoff/ledger
  contracts and machine-readable proof artifacts. Schemas live in
  `schema/extensions/`. The validator activates them only when the
  repository already contains those documents. A simple application does
  not need Evidence.

If a project does not perform multi-agent task orchestration with audit
trails, ignore Evidence entirely.

## Status

Public early draft. Current version: see [VERSION](VERSION). Release notes
in [CHANGELOG.md](CHANGELOG.md). The stable integration point is
`coad check .`.

## See also

- [STANDARD.md](STANDARD.md) — the standard.
- [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) — single-page agent recipe.
- [docs/validator.md](docs/validator.md) — full validator behavior.
- [docs/landscape.md](docs/landscape.md) — adjacent projects.
- [docs/demo-transcripts.md](docs/demo-transcripts.md) — reproducible demo output.
- [examples/before-after/](examples/before-after/) — fail/pass demo.
- [docs/archive/](docs/archive/) — v0.7.7 prose (principles, agent flow,
  adoption guide, project-standard, glossary). Useful as background, not
  required for adoption.
