# Module Contract Semantic Checklist

`coad check .` can verify that a `MODULE_CONTRACT.md` exists and follows the
expected structure. This checklist answers the harder question:

```text
Can an agent safely edit this module using this contract?
```

Use it when writing, reviewing, or updating a module contract.

In COAD terminology, the contracted module is a workcell: the smallest
independently ownable, documentable, and verifiable unit of agent work.

## Minimum Passing Bar

A good `MODULE_CONTRACT.md` lets a new agent answer these questions in two
minutes:

- What does this module own?
- What does this module explicitly not own?
- Is this workcell leaf, composite, or project-level?
- Who has write authority, and is the write lease exclusive?
- Which surfaces can other modules rely on?
- Who consumes those surfaces?
- Which invariants must not be broken?
- Which dependencies are allowed, and why?
- What can the agent change without escalation?
- What must the agent not change without escalation?
- Which commands prove the module is still correct?
- What known gaps or pending tasks remain?

If the contract cannot answer those questions, it is present but not useful.

## Semantic Checks

### Workcell Shape

- The contract makes clear whether the workcell is project, composite, or leaf.
- Leaf workcells can be edited by one write agent without understanding the
  whole repository.
- Composite workcells name child workcells and act as orchestration boundaries,
  not as places where parent agents edit child implementation directly.
- Cross-workcell changes require an explicit migration lease.

### Boundary

- Purpose is specific enough to exclude neighboring responsibilities.
- The module boundary names both owned behavior and out-of-scope behavior.
- The architecture section explains data flow, lifecycle, and tradeoffs at the
  level needed for a safe edit.

### Surfaces

- Every public or cross-module surface has a behavioral promise.
- Each surface names at least one consumer or clearly states that it is unused,
  experimental, or internal.
- Each important surface has proof: unit test, integration test, contract test,
  schema, golden file, static check, or an explicit missing-proof note.

### Dependencies

- Internal dependencies explain scope and reason, not just names.
- External dependencies are listed when they shape behavior, failure modes, or
  verification.
- The contract makes accidental cross-layer coupling visible.

### Invariants

- Invariants describe rules that would create real defects if broken.
- Each invariant has proof or an honest missing-proof marker.
- Preconditions are written as operational rules an agent can preserve.

### Verification

- `pre_change` commands are fast enough to run before editing or during a small
  loop.
- `full` commands are sufficient to support a completion claim.
- Commands are copy-pasteable from the module context.
- Manual proof is reserved for cases where automation is genuinely unavailable.

### Agent Policy

- Allowed mutations are concrete enough to guide work scope.
- Forbidden mutations name risky changes, not generic cautions.
- Escalation conditions cover boundary changes, public API changes, data loss,
  security-sensitive changes, and unclear ownership.
- Write authority is exclusive for leaf workcells.
- Read-only agents are allowed for investigation, review, and verification
  without taking the write lease.

### Context Budget

- The workcell stays within the repository's advisory context budget.
- README, TODO, and contract files are short operating briefs, not long essays.
- If the contract lists many unrelated surfaces or invariants, the workcell has
  a split candidate.
- Any budget exception names the exact metric and gives a reason an agent can
  use to decide whether to split, shrink, or proceed.
- If an agent cannot orient in two minutes, size or documentation is failing.

### Local Docs

- The module `README.md` explains the module to humans and agents.
- The module `TODO.md` lists real current gaps, not stale aspirations.
- The contract, README, and TODO do not contradict each other.

## Bad Smells

- The purpose could describe three different modules.
- The workcell is too large for one agent to hold in context.
- Budget exceptions exist without a reason, or become permanent hiding places
  for modules that should be split.
- Surfaces are listed as names without behavioral promises.
- Consumers are missing, vague, or wrong.
- Proof commands are absent, stale, or only test unrelated behavior.
- Invariants repeat style preferences instead of correctness rules.
- Allowed mutations say "anything in this folder".
- Two write agents are expected to work in the same leaf workcell concurrently.
- Forbidden mutations say "be careful" without naming concrete risks.
- The contract reads like documentation for humans but not like an operating
  brief for an agent.

## Update Triggers

Update the module contract when:

- a public or cross-module surface changes;
- a dependency is added, removed, or changes responsibility;
- a new invariant is discovered during debugging;
- verification commands change;
- ownership or safe write scope changes;
- workcell parent, children, authority, or context budget changes;
- a TODO becomes done, blocked, or obsolete;
- review finds an agent misunderstood the module boundary.

## Review Rule

The final review question is:

```text
Would I trust a fresh agent to make a small change in this module using only
the root guidance, this contract, the local README, and the local TODO?
```

If not, improve the contract before expanding automation.
