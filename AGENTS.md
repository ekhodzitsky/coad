# COAD Agent Guide

This repository contains the COAD methodology — written guidance for
coding-agent work. It is prose only: no CLI, no JSON schemas, no
runnable code.

If you are a coding agent inside this repository, your job is to keep
the prose coherent. The standard for that is judgment, not automation.

For a repository adopting COAD, the minimum agent recipe lives in
[AGENT_ONBOARDING.md](AGENT_ONBOARDING.md). The principles live in
[PRINCIPLES.md](PRINCIPLES.md); the body (vocabulary, lifecycle, worked
examples, when-to-use, integration) lives in [SPEC.md](SPEC.md).

## House rules for changes here

- Edits should make the methodology clearer, not longer.
- Do not add `MUST`/`SHALL`. COAD is recommendations.
- Do not introduce executable code, JSON schemas, or build tooling.
  This repository is prose.
- Keep the root file count small. README, PRINCIPLES, SPEC,
  AGENT_ONBOARDING, AGENTS, CHANGELOG is enough.
