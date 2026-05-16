# Adoption Smoke Tests

COAD should be usable by giving an agent one public link:

```text
https://github.com/ekhodzitsky/coad
```

The agent should then read the methodology, choose one real workcell in the
target repository, add minimal local context, run the target workcell proof,
and finish with:

```bash
coad check .
```

This page records real adoption smoke tests so onboarding quality is measured
against repositories, not only examples.

## phonex

Repository: `https://github.com/ekhodzitsky/phonex`

Date: 2026-05-16

Target workcell: `src/inference`

Why this workcell:

- it is already a coherent Rust subsystem;
- it owns local ONNX inference, audio decode/resampling, feature extraction,
  session pooling, greedy decode, and transcription result assembly;
- it has real public surfaces consumed by `src/lib.rs`, server handlers, and
  tests;
- it is small enough to document as one leaf workcell.

Baseline command:

```bash
uvx --from 'git+https://github.com/ekhodzitsky/coad.git#subdirectory=tools/coad-validator' coad check .
```

Baseline result:

```text
coad check: fail
```

The structured issue was `agent-guidance.failed` because the repository had no
`AGENTS.md` with COAD onboarding guidance.

Minimal adoption files:

```text
AGENTS.md
src/inference/MODULE_CONTRACT.md
src/inference/README.md
src/inference/TODO.md
```

Resulting size:

```text
16  AGENTS.md
140 src/inference/MODULE_CONTRACT.md
28  src/inference/README.md
8   src/inference/TODO.md
192 total
```

Validator feedback during adoption:

- invalid YAML in `purpose` when a colon was left unquoted;
- unsupported proof kind `manual-review`;
- public surfaces without declared consumers.

These were useful failures. They turned a present contract into a more
agent-useful contract without requiring a new command.

Final checks:

```bash
uvx --from 'git+https://github.com/ekhodzitsky/coad.git#subdirectory=tools/coad-validator' coad check .
cargo check --all-targets
git diff --check
```

Final `coad check` result:

```text
coad check: pass
```

Outcome:

- one-link validator installation worked from the public COAD repository;
- one real workcell was enough for initial adoption;
- semantic validation caught actionable contract quality issues;
- the chosen proof command was executable in a clean clone;
- no full-repository migration was needed.
