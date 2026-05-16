# Agent Guide

Use COAD for agent development coordination.

COAD repository: https://github.com/ekhodzitsky/coad

Before editing, identify the relevant workcell and read its
`MODULE_CONTRACT.md`, `README.md`, and `TODO.md`.

Before claiming completion:

```bash
coad check .
```

One leaf workcell may have only one active write agent. Read-only agents may
investigate, review, or verify in parallel. Composite workcell agents orchestrate
child work but do not directly edit child implementation files.

Keep at least one `MODULE_CONTRACT.md` for the module being changed. The module
is a workcell: one bounded agent workspace with ownership, surfaces, consumers,
invariants, verification, and write authority. The module directory must include
`README.md` and `TODO.md` for future agents.
