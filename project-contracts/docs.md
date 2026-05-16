---
schema_version: 1
kind: module_contract
module: docs
level: root
layer: methodology
purpose: Explain COAD adoption, orchestration rules, reports, and operating model.
status: pilot
owners:
  - methodology-maintainers
surface:
  - name: MethodologyDocs
    kind: documentation-api
    visibility: public
    contract: Gives agents and humans the current COAD workflow and rationale.
    proof:
      kind: static-check
      target: docs
      command: coad check .
dependencies:
  internal:
    - module: contracts
      scope: contract semantics
      reason: Documentation must describe the canonical methodology.
    - module: schema
      scope: report and contract shape
      reason: Documentation must match executable schemas.
    - module: tools/coad-validator
      scope: public command behavior
      reason: Documentation must match `coad check .`.
  external: []
consumers:
  - path: AGENTS.md
    uses:
      - MethodologyDocs
  - path: README.md
    uses:
      - MethodologyDocs
invariants:
  - id: public-command-stays-small
    rule: Public integration docs describe `coad check .` as the only utility command.
    proof:
      kind: static-check
      target: docs
      command: rg "coad-(validate|pack|status|proof|graph|schedule|ledger|profile|policy|attest|export|drift)" README.md ADOPTION.md GETTING_STARTED.md docs tools/README.md tools/coad-validator/README.md
verification:
  pre_change:
    - coad check .
  full:
    - uv run --locked pytest
    - coad check .
agent_policy:
  allowed_mutations:
    - Clarify adoption, operating model, and internal report semantics.
  forbidden_mutations:
    - Reintroduce public `coad-*` command guidance outside internal code/tests.
  escalation:
    - Public adoption flow change
    - New public command
---

# docs

The docs module owns COAD's explanatory surface and adoption guidance.
