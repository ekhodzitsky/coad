# COAD Agent Guide

This repository defines the **COAD methodology** — Contract-Orchestrated
Agent Development. It is a book, not a tool: no CLI, no schemas, no
validator.

If you are a coding agent inside this repository, your job is to keep
the prose coherent. The standard for that is judgment, not automation.

For a repository adopting COAD, the minimum agent recipe lives in
[AGENT_ONBOARDING.md](AGENT_ONBOARDING.md). The methodology itself lives
in [PRINCIPLES.md](PRINCIPLES.md). Background prose, validators, and
schemas from earlier drafts are in [docs/archive/](docs/archive/).

## House rules for changes here

- Edits should make the methodology clearer, not longer.
- Do not add `MUST`/`SHALL`. COAD is recommendations.
- Do not reintroduce the validator, JSON schemas, or executable
  examples without a discussion. They were intentionally archived in
  v0.9.0.
- Keep the root file count small. README, PRINCIPLES, AGENT_ONBOARDING,
  AGENTS, CHANGELOG, VERSION is enough.
