# Agent Flow

This is the default way an agent works inside a COAD-native repository.

The flow optimizes for fast orientation, bounded edits, proof-backed handoff,
and safe parallel work. `coad check .` validates the methodology; it is not the
orchestrator.

## Entry Protocol

1. Read root `AGENTS.md`.
2. Locate the relevant module contract.
3. Read the module `README.md`.
4. Read the module `TODO.md`.
5. Identify surfaces, consumers, invariants, and proof commands.
6. Define read scope and write scope before editing.
7. Inspect implementation only after the boundary is clear.

The agent should enter through contracts and local context, not through a broad
repository search.

## Two-Minute Orientation Checklist

Before editing, the agent should be able to answer:

- Which module owns this behavior?
- Which files am I allowed to change?
- Which files may I read for context?
- Which surface am I changing or preserving?
- Which consumers could be affected?
- Which invariants must remain true?
- Which proof commands will establish correctness?
- Does this require updating a contract, README, TODO, schema, or docs?

If these answers are unclear, the agent should clarify the module context before
changing code.

## Work Protocol

1. Lock the intended write scope.
2. Read the focused implementation files.
3. Add or identify proof before changing shared behavior.
4. Make the smallest change that satisfies the task.
5. Update module context if ownership, surfaces, dependencies, consumers,
   invariants, or verification changed.
6. Run focused proof.
7. Run broader verification when the change touches shared behavior.
8. Run `coad check .` before claiming the repository still follows COAD.

Small documentation-only changes may use lighter proof, but they still must not
invalidate module context.

## Parallel Agent Protocol

A lead agent or orchestrator should assign parallel work by module ownership:

1. Decompose the goal into module-owned tasks.
2. Give each agent the relevant module contract, README, TODO, and proof
   expectations.
3. Ensure write scopes do not overlap.
4. Serialize tasks that touch the same invariant, public surface, schema, or
   shared dependency.
5. Require proof-backed handoff from each agent.
6. Integrate only after handoffs, proof, and review are complete.

Parallel work is safe when agents operate inside clear boundaries. It is unsafe
when they merely edit different files without knowing shared invariants.

## Change Classification

Use the smallest class that honestly describes the change:

- **Documentation-only:** text changes that do not alter contracts, behavior, or
  public guidance.
- **Internal refactor:** implementation changes that preserve surfaces and
  behavior.
- **Behavior change:** user-visible or consumer-visible behavior changes.
- **Public surface change:** API, schema, event, CLI, protocol, report, or data
  shape changes.
- **Dependency change:** new, removed, or upgraded internal/external dependency.
- **Invariant change:** adds, weakens, removes, or redefines a module promise.

Higher-risk classes require stronger proof and usually contract updates.

## Handoff Template

Use this shape when handing work to another agent, reviewer, or integrator:

```markdown
Module:
Write scope:
Changed files:
Contracts/context updated:
Surfaces changed:
Consumers affected:
Invariants checked:
Proof run:
Known gaps:
Recommended next step:
```

The handoff should be useful without the sender's chat history.

## Review Protocol

A reviewer checks the contract before the diff:

1. Does the change stay inside declared module ownership?
2. Did it alter public or internal surfaces?
3. Are consumers updated or explicitly unaffected?
4. Are invariants preserved?
5. Is proof strong enough for the change class?
6. Did module context change when the module changed?

Review should convert uncertainty into explicit follow-up work, not hidden
acceptance.

## What Agents Should Avoid

- Starting with a whole-repo scan when a module contract exists.
- Editing across module boundaries without updating ownership context.
- Changing public surfaces without naming affected consumers.
- Reporting completion without proof output.
- Leaving local TODO or README stale after changing module behavior.
- Treating `coad check .` as a substitute for understanding the module.

The best COAD agent is not the agent that reads the most. It is the agent that
enters through the right boundary, changes the smallest safe scope, proves the
claim, and leaves the next agent a better map.
