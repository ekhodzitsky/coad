# COAD Agent Guide

This repository defines Contract-Orchestrated Agent Development.

Minimum onboarding for any repository adopting COAD:

1. Paste this guide into `AGENTS.md`.
2. Add one `MODULE_CONTRACT.md` for a real module.
3. Ensure that module has `README.md` and `TODO.md`.
4. Run `coad check .`.

Agents changing this repository must keep the public utility surface focused on
`coad check .` and update the methodology docs when the check semantics change.

This repository dogfoods COAD through `project-contracts/`. When changing a
real project module such as `contracts/`, `schema/`, `docs/`, `templates/`,
`examples/`, `playbooks/`, or `tools/coad-validator/`, keep that module's
contract plus local `README.md` and `TODO.md` current.

Use `COAD_PROJECT_STANDARD.md` as the source of truth for COAD-native project
shape and `AGENT_FLOW.md` as the source of truth for how agents enter, change,
prove, and hand off work.
