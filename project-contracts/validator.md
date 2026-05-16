---
schema_version: 1
kind: module_contract
module: tools/coad-validator
level: root
layer: tooling
purpose: Implement the lightweight `coad check .` utility and internal report builders.
status: pilot
owners:
  - validator-maintainers
surface:
  - name: coad check
    kind: cli
    visibility: public
    contract: Runs the progressive COAD methodology compliance check.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests/test_check.py
      command: uv run --locked pytest tests/test_check.py
dependencies:
  internal:
    - module: schema
      scope: validation schemas
      reason: The checker executes schema validation.
    - module: docs
      scope: public behavior
      reason: CLI behavior must match adoption docs.
  external:
    - name: jsonschema
      scope: Draft 2020-12 validation
      reason: Contract and report schemas need standard validation.
    - name: pyyaml
      scope: Markdown frontmatter parsing
      reason: Contract files use YAML frontmatter.
consumers:
  - path: .github/workflows/ci.yml
    uses:
      - coad check
  - path: GETTING_STARTED.md
    uses:
      - coad check
invariants:
  - id: one-public-command
    rule: The package exposes only the `coad` console script and the public subcommand is `check`.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests/test_check.py
      command: uv run --locked pytest tests/test_check.py
verification:
  pre_change:
    - uv run --locked pytest tests/test_check.py
  full:
    - uv run --locked pytest
    - coad check .
agent_policy:
  allowed_mutations:
    - Improve checker behavior while preserving one-line text output.
  forbidden_mutations:
    - Add new public console scripts without changing the methodology contract.
  escalation:
    - New public CLI command
    - Check semantics that block the two-minute onboarding path
---

# tools/coad-validator

The validator module owns the executable `coad check .` integration surface.
