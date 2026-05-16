# COAD Agent Onboarding

If a user sent you this repository link, they should not need to paste snippets,
copy templates, or wire COAD by hand.

Your job as the agent is to adopt COAD in the target repository, make the
minimal useful changes, and prove the result with:

```bash
coad check .
```

## Agent Task

1. Read this file, `README.md`, `COAD_PROJECT_STANDARD.md`, `AGENT_FLOW.md`, and
   `docs/workcells.md`.
2. Inspect the target repository and choose one real module/workcell that is
   worth documenting first.
3. Add or update the target repository `AGENTS.md` with COAD guidance.
4. Add one `MODULE_CONTRACT.md` for that real workcell.
5. Ensure the workcell has `README.md` and `TODO.md`.
6. Run the workcell verification commands listed in `MODULE_CONTRACT.md`.
7. Run `coad check .`.
8. Fix any reported COAD adoption issues.
9. Report changed files, selected workcell, verification output, and remaining
   adoption gaps.

Do not ask the user to paste files manually. Ask only when repository access,
network access, package installation, or write authority is blocked.

## Validator

The COAD repository is public. Run the validator directly from the public HTTPS
URL:

```bash
uvx --from 'git+https://github.com/ekhodzitsky/coad.git#subdirectory=tools/coad-validator' coad check .
```

If `coad` is already installed:

```bash
coad check .
```

If you are working from a local COAD clone:

```bash
uvx --from /path/to/coad/tools/coad-validator coad check /path/to/target/repository
```

The validator bundles COAD schemas. Do not copy this repository's `schema/`
directory into the target project unless the user explicitly wants to vendor
schemas.

If network or Python package tooling prevents the command from running, report
that as an onboarding blocker instead of asking the user to perform manual
COAD setup.

## Minimal Target Shape

The smallest useful adoption looks like this:

```text
AGENTS.md
<workcell>/
  MODULE_CONTRACT.md
  README.md
  TODO.md
```

Choose a real workcell. Good first choices have clear ownership, real consumers,
fragile invariants, public surfaces, side effects, or frequent edits.

Avoid creating a fake `example` module only to satisfy the checker.

## AGENTS.md Guidance

Add this guidance to the target repository `AGENTS.md`, preserving existing
local instructions:

````markdown
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
````

## Workcell Files

Start from `templates/onboarding/MODULE_CONTRACT.md` when possible, but adapt it
to the target repository instead of copying placeholders.

The workcell `README.md` should be a short operating brief:

```markdown
# <workcell>

## Purpose
## Surfaces
## Dependencies
## Invariants
## Verification
## Notes
```

The workcell `TODO.md` should stay current:

```markdown
# <workcell> TODO

## Current
## Next
## Known Gaps
## Deferred
```

## Done

COAD onboarding is done when:

- the target repository has COAD guidance in `AGENTS.md`;
- at least one real workcell has `MODULE_CONTRACT.md`, `README.md`, and
  `TODO.md`;
- the selected workcell verification commands have been run or explicitly
  reported as blocked;
- `coad check .` passes;
- the handoff tells the user what was adopted and what remains outside the
  initial workcell.
