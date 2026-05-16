---
schema_version: 1
kind: task_contract
task_id: <task-id>
objective: <one sentence objective>
owner_role: <agent role or human owner>
status: pending
risk: <low|medium|high|critical>
change_class: <documentation_only|internal_refactor|behavior_change|public_surface_change|dependency_change|invariant_change|security_privacy_change|performance_sensitive_change>
modules:
  - <module-id>
read_scope:
  - <path or module surface>
write_scope:
  - <path or module surface>
dependencies: []
allowed_mutations:
  - <allowed mutation>
forbidden_mutations:
  - <forbidden mutation>
acceptance:
  - <observable acceptance criterion>
proof:
  required:
    - proof_id: <proof-id>
      kind: <proof-kind>
      target: <target>
      command: <command>
handoff:
  required_fields:
    - changed_files
    - proof_results
    - contract_updates
    - known_gaps
---

# <task-id>

## Context

Explain only what the worker needs to execute this task safely.

## Exit Criteria

List exact conditions for complete, blocked, or not_ready.
