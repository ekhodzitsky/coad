# COAD

**Contract-Orchestrated Agent Development** — a methodology for keeping
coding-agent work safe, reviewable, and bounded.

This repository is a book, not a tool. It does not ship a CLI, a JSON
schema, or a validator. It ships prose: principles, agent flows,
contract patterns, and adoption guidance. The way you apply COAD is up
to you and your agents.

## What COAD is for

When coding agents edit a non-trivial repository, they can change files
across invisible ownership boundaries, break consumers that no one
remembered to mention, and report "done" without proof. COAD names the
pieces that prevent that:

- **Module contracts** — small local files beside the code that say what
  the module owns, what it exposes, who depends on it, and how to prove
  it still works.
- **Workcells** — the smallest independently ownable, documentable, and
  verifiable unit of agent work.
- **Proof-backed handoffs** — durable artifacts (not chat summaries)
  that let the next agent or human pick up without context loss.
- **Bounded parallel work** — one leaf workcell, one active write
  agent. Read-only investigation is unbounded.

The [principles](PRINCIPLES.md) state the ten rules the methodology
rests on. The [agent onboarding](AGENT_ONBOARDING.md) page is the page
you give to a coding agent when you want it to start working under COAD.

## What COAD is not

- Not a tool. There is no `coad check`. If you want automation, build
  it.
- Not a workflow runtime. COAD does not run, schedule, or dispatch
  agents.
- Not a spec with `MUST`/`SHALL` clauses. Every guideline here is a
  recommendation. The decision to keep an invariant strict belongs to
  the team that owns the module.
- Not a replacement for code review or judgment.

## How to adopt it

There is no install step.

1. Read [PRINCIPLES.md](PRINCIPLES.md). Decide which ones apply to your
   project.
2. Pick one real module that hurts when an agent edits it blindly.
3. Write a `MODULE_CONTRACT.md` for that module — purpose, surfaces,
   consumers, invariants, proof commands. Keep it short.
4. Add `README.md` and `TODO.md` next to it. Keep them current.
5. When you give a task to an agent, point it at that contract first.

That is the whole adoption path. Nothing else is required.

## Status

Public early draft. Release notes: [CHANGELOG.md](CHANGELOG.md). The
methodology is stabilising; expect the prose to keep moving as we learn
from real adoption. Earlier drafts (validator, JSON schemas, longer
specification prose) are preserved in git history at tags before
`v0.9.0`.

## See also

- [PRINCIPLES.md](PRINCIPLES.md) — the ten principles.
- [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) — single-page agent recipe.
