# Contributing to COAD

Thanks for considering a change. This repository contains the COAD
methodology — written guidance for coding-agent work. It is prose only:
no CLI, no JSON schemas, no runnable code.

## Scope of contributions

Welcome:

- Clarifications in `PRINCIPLES.md`, `SPEC.md`, or `README.md`.
- New or improved worked examples in `SPEC.md §6`.
- Sharper «when not to use COAD» bullets in `SPEC.md §8`.
- Adoption reports — open an issue describing what worked, what did
  not, and which parts you skipped.

Not welcome without prior discussion:

- Executable code, JSON schemas, or build tooling. The methodology was
  intentionally collapsed to prose in v0.9. Open an issue first if you
  think automation is needed.
- Renaming terms in `SPEC.md §1` without updating every reference.
- Adding `MUST` / `SHALL` clauses. COAD is recommendations, not RFC.

## House rules

- Edits should make the methodology clearer, not longer.
- Keep the root file count small. README, PRINCIPLES, SPEC,
  AGENT_ONBOARDING, CONTRIBUTING, CHANGELOG, LICENSE is enough.
- Update `CHANGELOG.md` for any user-visible change.
- For AI agents working in this repository: this file is for human
  contributors; the recipe for an agent that adopts COAD in *another*
  repository lives in `AGENT_ONBOARDING.md`.

## Pull requests

- One concept per PR. A clarification, a new example, and a
  vocabulary change are three PRs, not one.
- The PR description should answer: «what was confusing or missing
  before this change?»
- No commit signature is required, but a Co-Authored-By line is
  welcome when the change is collaborative.
