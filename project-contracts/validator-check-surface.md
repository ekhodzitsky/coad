---
schema_version: 1
kind: module_contract
module: validator/check-surface
level: subsystem
layer: tooling
purpose: Own the public `coad check .` command surface and check aggregation.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: tools/coad-validator
  context_path: tools/coad-validator
  children: []
  owns_paths:
    - tools/coad-validator/src/coad_validator/agent_guidance.py
    - tools/coad-validator/src/coad_validator/check.py
    - tools/coad-validator/src/coad_validator/cli.py
    - tools/coad-validator/src/coad_validator/coad_cli.py
    - tools/coad-validator/src/coad_validator/report.py
    - tools/coad-validator/src/coad_validator/report_sources.py
  context_budget:
    max_files: 12
    max_source_lines: 1500
    max_contract_lines: 180
    max_readme_lines: 120
    max_todo_lines: 80
    max_surfaces: 8
    max_invariants: 8
authority:
  write_policy: single_active_write_lease
  orchestrator: tools/coad-validator
  read_agents: many_allowed
surface:
  - name: coad check
    kind: cli
    visibility: public
    contract: Runs the single public COAD methodology check command.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests/test_check.py
      command: uv run --locked pytest tests/test_check.py
dependencies:
  internal:
    - module: validator/core
      scope: validation report
      reason: The public command wraps core validation and report sources.
  external: []
consumers:
  - path: README.md
    uses:
      - coad check
invariants:
  - id: one-public-command
    rule: The utility exposes `coad check` as the only public workflow command.
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
---

# validator/check-surface

Owns public CLI behavior and check aggregation.
