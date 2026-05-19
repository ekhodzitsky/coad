---
schema_version: 1
kind: module_contract
module: validator/bundled-manifest-schemas
level: subsystem
layer: tooling
purpose: Keep bundled manifest schemas and manifest data in sync with canonical files.
status: pilot
owners:
  - validator-maintainers
workcell:
  type: leaf
  parent: tools/coad-validator
  context_path: tools/coad-validator
  children: []
  owns_paths:
    - tools/coad-validator/src/coad_validator/schema/extensions/conformance-profile.schema.json
    - tools/coad-validator/src/coad_validator/schema/lease-manifest.schema.json
    - tools/coad-validator/src/coad_validator/schema/release-manifest.json
    - tools/coad-validator/src/coad_validator/schema/release-manifest.schema.json
    - tools/coad-validator/src/coad_validator/schema/report-manifest.json
    - tools/coad-validator/src/coad_validator/schema/report-manifest.schema.json
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
  - name: BundledManifestSchemas
    kind: schema-set
    visibility: internal
    contract: Provides packaged release, report, and lease manifest schemas.
    proof:
      kind: schema
      target: tools/coad-validator/src/coad_validator/schema
      command: jq empty tools/coad-validator/src/coad_validator/schema/*.json tools/coad-validator/src/coad_validator/schema/reports/*.json
dependencies:
  internal:
    - module: schema/manifests
      scope: canonical manifests
      reason: Bundled manifests must match canonical files.
  external: []
consumers:
  - path: tools/coad-validator/src/coad_validator/drift.py
    uses:
      - BundledManifestSchemas
invariants: []
verification:
  pre_change:
    - jq empty tools/coad-validator/src/coad_validator/schema/*.json tools/coad-validator/src/coad_validator/schema/reports/*.json
  full:
    - uv run --locked pytest
    - coad check .
---

# validator/bundled-manifest-schemas

Owns bundled manifest schemas and manifest data.
