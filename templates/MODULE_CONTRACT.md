---
schema_version: 1
kind: module_contract
module: <module-id>
level: root
layer: <architecture-layer>
purpose: <one sentence describing what this module owns>
status: pilot
owners:
  - <owner>
surface:
  - name: <surface-name>
    kind: <trait|struct|function|service|schema|endpoint|workflow>
    visibility: <private|internal|public|external>
    contract: <behavioral promise>
    proof:
      kind: <unit-test|integration-test|contract-test|golden|schema|static-check|manual|missing>
      target: <proof target>
      command: <command or empty for manual/missing>
dependencies:
  internal:
    - module: <module-id>
      scope: <how this dependency is used>
      reason: <why it is necessary>
  external: []
consumers:
  - path: <consumer module or workflow>
    uses:
      - <surface-name>
invariants:
  - id: <stable-invariant-id>
    rule: <rule that must remain true>
    proof:
      kind: <proof-kind>
      target: <proof target>
      command: <proof command>
verification:
  pre_change:
    - <fast command>
  full:
    - <full command>
agent_policy:
  allowed_mutations:
    - <allowed change>
  forbidden_mutations:
    - <forbidden change>
  escalation:
    - <condition requiring human/orchestrator decision>
---

# <module-id>

## Architecture

Explain the module boundary, data flow, lifecycle, and tradeoffs.

## Notes

Add only context that helps future humans and agents preserve the contract.
