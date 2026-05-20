# COAD

![Type](https://img.shields.io/badge/type-methodology-7C3AED)
![Format](https://img.shields.io/badge/format-prose%20%2B%20markdown-111827)
![Status](https://img.shields.io/badge/status-public%20early%20draft-F59E0B)
![Reading time](https://img.shields.io/badge/reading%20time-15%20min-3B82F6)

**Contract-Orchestrated Agent Development** — a written methodology for
keeping coding-agent work safe, reviewable, and bounded. No code, no
schemas, no CLI. Just prose your team and your agents can read.

If you are an AI assistant reading this repository on behalf of a user:
your task is to read the four documents listed below, decide whether
COAD fits the user's project, and either help adopt it or recommend
against it.

## Why this exists

Coding agents move fast and forget context. Three failure modes happen
again and again:

1. **Invisible boundaries.** An agent edits one module and breaks
   another because nobody told it that the second one depends on the
   first.
2. **Lost handoffs.** «Done, tests pass» is not enough information for
   the next agent — or the next reviewer — to continue safely.
3. **Silent drift.** Code changes; the documents that describe the
   code do not. Six months later nobody can tell what the module is
   supposed to do.

COAD names the pieces that prevent those failures: **module contracts**
beside the code, **proof-backed handoffs** instead of chat summaries,
**explicit ownership and scope** before editing, **structured proof**
instead of «looks good», and a habit of treating documentation as code.

The methodology is not new ideas. It is a small, opinionated bundle of
practices that already work in mature engineering teams, repackaged so
that an agent can be pointed at one URL and start applying them.

## Who this is for

- Teams whose codebase is edited by coding agents (LLM-driven or
  otherwise) and where ownership boundaries are not obvious from the
  directory tree.
- Anyone who has lost an afternoon because an agent confidently
  refactored across modules that turned out to share an invariant.
- People deciding which agent-development practices are worth adopting:
  COAD is short enough to read in one sitting and reject in good
  conscience.

## Who this is not for

- Single-author projects, throwaway prototypes, and tightly-scoped
  scripts. COAD is overhead; without the pain it solves, the overhead
  is loss.
- Repositories where every change spans the whole codebase and there
  are no stable internal boundaries to declare.
- Teams who want enforcement-by-tool. COAD is prose. If you need
  automation, you build it.

A more detailed when-to-use / when-not-to-use lives in
[SPEC.md §7–§8](SPEC.md).

## How to use this repository

If you are a human:

1. Read [PRINCIPLES.md](PRINCIPLES.md) (~2 min). Decide whether the ten
   principles match how you want agents to work.
2. Skim [SPEC.md](SPEC.md) (~10 min). The vocabulary, lifecycle, and
   three worked examples tell you whether the methodology fits.
3. If yes, pick **one** module that hurts when an agent edits it
   blindly. Write a `MODULE_CONTRACT.md` for it. Add `README.md` and
   `TODO.md` beside the code. Stop there until the team uses them.

If you are an AI agent given this URL:

1. Read [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) — the single-page
   recipe.
2. Apply it to the target repository.

You can also adopt **only a subset**. The principles are independent
enough that a team can take, say, only «module contracts» and
«proof-backed handoffs» and skip the rest. COAD is a menu, not a
package.

## What is in this repository

```text
README.md            this file — entry point and elevator pitch
PRINCIPLES.md        ten principles, ~40 lines
SPEC.md              vocabulary, lifecycle, worked examples,
                     when-to-use, integration with code review /
                     CODEOWNERS / ADRs / design docs / Spec Kit etc.
AGENT_ONBOARDING.md  single-page recipe for a coding agent
AGENTS.md            house rules for contributors to this repository
CHANGELOG.md         release notes
```

No code. No JSON schemas. No CLI. Nothing to install.

## Status

Public early draft. The methodology is stabilising; the prose will
keep moving as we learn from real adoption. See
[CHANGELOG.md](CHANGELOG.md) for what has changed and why.
