---
schema_version: 1
kind: module_contract
module: docs/reports-and-gates
level: subsystem
layer: methodology
purpose: Explain validator reports, release gates, proof matrices, ledgers, and export artifacts.
status: pilot
owners:
  - methodology-maintainers
workcell:
  type: leaf
  parent: docs
  context_path: docs
  children: []
  owns_paths:
    - docs/artifact-export.md
    - docs/attestation-bundle.md
    - docs/conformance-profile.md
    - docs/contract-graph.md
    - docs/execution-ledger.md
    - docs/policy-enforcement.md
    - docs/proof-matrix.md
    - docs/release-gates.md
    - docs/report-versioning.md
    - docs/tool-output-schemas.md
    - docs/validator.md
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
  orchestrator: docs
  read_agents: many_allowed
surface:
  - name: ReportAndGateDocs
    kind: documentation-api
    visibility: public
    contract: Describes COAD validator reports and release gates accurately enough for CI and agents.
    proof:
      kind: static-check
      target: docs/validator.md
      command: coad check .
dependencies:
  internal:
    - module: schema
      scope: report schemas
      reason: Report docs must match machine-readable schemas.
    - module: tools/coad-validator
      scope: report builders
      reason: Report docs must match validator output.
  external: []
consumers:
  - path: docs/validator.md
    uses:
      - ReportAndGateDocs
invariants: []
verification:
  pre_change:
    - coad check .
  full:
    - coad check .
---

# docs/reports-and-gates

Owns public documentation for validator output, release evidence, and report schemas.
