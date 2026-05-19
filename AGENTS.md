# COAD Agent Guide

This repository defines a standard for agent-navigable codebases.

Minimum onboarding for any repository adopting COAD:

1. Paste the COAD URL + the `AGENTS.md` snippet from
   [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) into your repo's `AGENTS.md`.
2. Add one `MODULE_CONTRACT.md` for a real module.
3. Ensure that module has `README.md` and `TODO.md`.
4. Run `coad check .`.

Agents changing this repository must keep the public utility surface
focused on `coad check .` and update [STANDARD.md](STANDARD.md) when the
check semantics change.

This repository dogfoods COAD through `project-contracts/`. When changing a
real project module such as `schema/`, `docs/`, `examples/`, or
`tools/coad-validator/`, keep that module's contract plus local `README.md`
and `TODO.md` current.

[STANDARD.md](STANDARD.md) is the source of truth for what
`coad check .` enforces. Pre-v2 prose (principles, agent flow, adoption
levels) lives in [docs/archive/](docs/archive/).
