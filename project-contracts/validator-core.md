---
schema_version: 1
kind: module_contract
module: validator/core
level: subsystem
layer: tooling
purpose: Own core contract discovery, schema validation, module context, budgets, semantic quality, lease manifests, and release metadata checks.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: tools/coad-validator
  context_path: tools/coad-validator
  children: []
  owns_paths:
    - tools/coad-validator/src/coad_validator/__init__.py
    - tools/coad-validator/src/coad_validator/frontmatter.py
    - tools/coad-validator/src/coad_validator/lease_manifest.py
    - tools/coad-validator/src/coad_validator/model.py
    - tools/coad-validator/src/coad_validator/module_context.py
    - tools/coad-validator/src/coad_validator/release_metadata.py
    - tools/coad-validator/src/coad_validator/schema.py
    - tools/coad-validator/src/coad_validator/semantic_quality.py
    - tools/coad-validator/src/coad_validator/validate.py
    - tools/coad-validator/src/coad_validator/workcell_budget.py
    - tools/coad-validator/src/coad_validator/workcell_graph.py
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
  - name: validate_path
    kind: python-api
    visibility: internal
    contract: Produces the canonical validation report used by `coad check .` and report builders.
    proof:
      kind: unit-test
      target: tools/coad-validator/tests/test_validator.py
      command: uv run --locked pytest tests/test_validator.py
dependencies:
  internal:
    - module: schema
      scope: JSON schemas
      reason: Core validation executes schemas.
  external:
    - name: jsonschema
      scope: schema validation
      reason: Contract schemas use Draft 2020-12.
    - name: pyyaml
      scope: frontmatter parsing
      reason: Contracts use YAML frontmatter.
consumers:
  - path: tools/coad-validator/src/coad_validator/check.py
    uses:
      - validate_path
invariants: []
verification:
  pre_change:
    - uv run --locked pytest tests/test_validator.py
  full:
    - uv run --locked pytest
    - coad check .
---

# validator/core

Owns the validator core behind `coad check .`.
