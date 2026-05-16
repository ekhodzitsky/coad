# Proof Matrix

The proof matrix maps change classes to required evidence.

## Change Classes

| Change class | Definition | Minimum proof |
| --- | --- | --- |
| `documentation_only` | Text changes that do not alter behavior or contracts. | Spell/check or format check when available. |
| `internal_refactor` | Implementation changes that preserve surface and behavior. | Existing regression tests for affected module. |
| `behavior_change` | User-visible or consumer-visible behavior changes. | New behavior test plus regression tests. |
| `public_surface_change` | API, schema, event, CLI, protocol, or exported surface changes. | Consumer proof, compatibility/migration evidence, docs update. |
| `dependency_change` | New, removed, or upgraded internal/external dependency. | Rationale, dependency risk check, full module verification. |
| `invariant_change` | Adds, weakens, removes, or redefines a module invariant. | Updated invariant proof plus review acceptance. |
| `security_privacy_change` | Auth, authorization, secrets, privacy, sandbox, or trust boundary changes. | Security review, negative tests, redaction/leak proof when relevant. |
| `performance_sensitive_change` | Latency, memory, throughput, or cost-sensitive changes. | Baseline and after measurement or benchmark. |

## Readiness Rule

A task cannot be accepted until all required proof for its change class passes or is explicitly accepted as missing proof debt by policy.

## Machine Report

Use `coad-proof-matrix` to inspect proof readiness independently from overall
goal or task readiness:

```bash
cd tools/coad-validator
uv run coad-proof-matrix ../.. --schema-dir ../../schema
```

The command emits JSON with every required task proof command, the referenced
proof contract, matching handoff evidence, and a per-proof status. This lets an
orchestrator distinguish "proof is satisfied" from "the task is declared ready".

The output is covered by `schema/reports/proof-matrix.schema.json`.

## Missing Proof

`kind: missing` is allowed during migration, but it is never silent success. It must include:

- what claim lacks proof;
- why proof is missing;
- risk of accepting the gap;
- owner or follow-up task;
- whether it blocks readiness.

## Proof Quality

Good proof is:

- tied to a claim;
- repeatable or explicitly manual;
- scoped to the changed contract;
- stored or summarized in handoff;
- strong enough for the risk.

Weak proof is:

- prose-only;
- broad but irrelevant;
- flaky without explanation;
- unowned;
- not runnable by the next worker.
