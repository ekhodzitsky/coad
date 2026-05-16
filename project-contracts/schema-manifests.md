---
schema_version: 1
kind: module_contract
module: schema/manifests
level: subsystem
layer: tooling-contract
purpose: Maintain manifest schemas and committed release/profile/lease manifests.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: schema
  context_path: schema
  children: []
  owns_paths:
    - schema/conformance-profile.schema.json
    - schema/lease-manifest.schema.json
    - schema/release-manifest.json
    - schema/release-manifest.schema.json
    - schema/report-manifest.json
    - schema/report-manifest.schema.json
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
  orchestrator: schema
  read_agents: many_allowed
surface:
  - name: ReleaseAndReportManifests
    kind: schema-set
    visibility: public
    contract: Defines release gate, report, and lease manifest structure.
    proof:
      kind: schema
      target: schema/*manifest*
      command: jq empty schema/*.json schema/reports/*.json
dependencies:
  internal:
    - module: tools/coad-validator
      scope: drift and profile checks
      reason: Manifests are consumed by validator report builders.
  external: []
consumers:
  - path: tools/coad-validator/tests/test_drift.py
    uses:
      - ReleaseAndReportManifests
invariants: []
verification:
  pre_change:
    - jq empty schema/*.json schema/reports/*.json
  full:
    - uv run --locked pytest
    - coad check .
---

# schema/manifests

Owns schemas and committed data for release/profile/report manifests.
