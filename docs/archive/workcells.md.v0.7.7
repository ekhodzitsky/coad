# Workcell Model

A COAD-native project is a tree of workcells.

A workcell is the smallest independently ownable, documentable, and verifiable
unit of agent work. It may map to a language module, package, service,
directory, feature area, or documentation area. The boundary is chosen by agent
comprehension and ownership, not by implementation naming alone.

`MODULE_CONTRACT.md` remains the compatibility filename for a workcell contract.
Conceptually, a module contract is a workcell contract.

`coad check .` validates the declared workcell tree: module identifiers must be
unique, parents and children must exist, child contracts must point back to
declared parents, parent cycles are invalid, leaf workcells cannot declare
children, and project/composite workcells cannot directly own descendant
implementation paths. It also rejects overlapping `owns_paths` between leaf
workcells.

## Workcell Types

### Project Workcell

The project workcell is the root of the repository. It owns global guidance,
top-level policy, shared verification, and the workcell tree.

The project workcell should stay small. It should route agents to local
workcells instead of replacing local context with a giant root README.

### Composite Workcell

A composite workcell contains child workcells.

Its assigned agent is an orchestrator. The orchestrator is read-only for child
implementation work. It may:

- read child contracts, README files, TODO files, and proof outputs;
- decompose goals into child-owned tasks;
- assign write leases to child workcells;
- serialize work that touches shared invariants or surfaces;
- accept or reject proof-backed handoffs;
- escalate conflicts to the parent orchestrator.

The composite orchestrator should not directly edit child implementation files.
If implementation must change, the change is delegated to the child workcell
that owns the affected surface.

### Leaf Workcell

A leaf workcell is the normal implementation unit.

It has one active write agent at a time. That agent owns local implementation
decisions inside the declared write scope and must preserve the contract,
README, TODO, surfaces, invariants, and proof expectations.

Leaf workcells are where most code changes should happen.

## Authority

Agent authority is scoped by workcell.

| Role | Scope | Write authority |
| --- | --- | --- |
| Root orchestrator | Project workcell | Global policy and orchestration artifacts only. |
| Composite orchestrator | One composite workcell | Its own orchestration artifacts; no direct child implementation writes. |
| Leaf write agent | One leaf workcell | One active write lease inside declared paths. |
| Read agent | Any assigned workcell | Read-only investigation, review, summarization, or verification. |

An agent that owns several workcells is an orchestrator, not a multi-module
implementation agent. It delegates writes downward to the workcell that owns
the affected behavior.

## Write Leases

A write lease is the temporary right to mutate a workcell.

Rules:

- A leaf workcell has at most one active write lease.
- Project and composite workcells orchestrate; they do not hold write leases.
- A write lease names at least the workcell, owner, mode, and write scope. It
  may also name the task, proof, expiry, or completion condition.
- Read-only agents may work in parallel without a write lease.
- A parent orchestrator may not bypass a child lease to edit child
  implementation directly.
- Sibling workcells may be edited in parallel only when their contracts,
  invariants, surfaces, and dependency order do not conflict.
- Leaf workcells may not have overlapping `owns_paths`. Shared files should
  become their own workcell or be owned by the nearest composite as an
  orchestration artifact, not as child implementation.

Active leases can be declared in `.coad/leases.yml`:

```yaml
version: 1
leases:
  - workcell: checkout
    owner: codex
    mode: write
    scope:
      - src/checkout/
```

`mode` is one of `read`, `orchestrate`, or `write`. A write lease without
`scope` means the workcell's full declared `owns_paths`. Optional `task`,
`proof`, `expires_at`, and `complete_when` fields carry handoff context without
becoming a runtime dependency. `coad check .` rejects unknown workcells, write
leases on composite workcells, duplicate write leases, overlapping write
scopes, and write scope outside declared ownership.

Separate git worktrees do not remove the need for a write lease. They prevent
file-level collisions, but they do not prevent two agents from making
incompatible architectural decisions inside the same ownership boundary.

## Migration Leases

Some changes legitimately cross workcell boundaries: schema migrations, public
API renames, dependency upgrades, formatting migrations, and shared protocol
changes.

These require a migration lease approved by the nearest common orchestrator.

A migration lease must name:

- every affected workcell;
- why ordinary leaf-local work is insufficient;
- the temporary write scope;
- which child owners must be notified or paused;
- proof required for each affected workcell;
- the integration owner.

Migration leases are exceptions, not the default parallel development model.

## Context Budgets

A workcell must fit into an agent's working context.

Default advisory budgets:

| Budget | Suggested maximum |
| --- | ---: |
| Source files in normal edit scope | 12 |
| Source lines in normal edit scope | 1500 |
| `MODULE_CONTRACT.md` lines | 180 |
| `README.md` lines | 120 |
| `TODO.md` lines | 80 |
| Public or cross-workcell surfaces | 8 |
| Invariants | 12 |
| Active write agents | 1 |

These are not universal laws. A repository may tune them, but a larger budget
must be justified by evidence that agents can still orient quickly and safely.
`coad check .` treats declared budget overruns as failures unless the contract
records a visible `budget_exceptions` reason.

The two-minute orientation rule is stronger than any numeric budget: if a fresh
agent cannot understand the workcell boundary, surfaces, risks, and proof in
two minutes, the workcell is too large or under-documented.

## Split Triggers

Split a workcell when:

- its README becomes an encyclopedia instead of an operating brief;
- the contract needs many unrelated surfaces or invariants;
- two independent changes frequently need to edit it at the same time;
- agents repeatedly need broad repository scans before local edits;
- the workcell owns multiple unrelated lifecycles or data flows;
- proof for one surface requires unrelated subsystems;
- safe write scope cannot be described concretely.

Prefer a shallow tree. A flat set of well-sized leaf workcells is usually
better than a deep hierarchy. Add composite workcells only when orchestration,
shared invariants, or ownership boundaries need them.

## Required Local Context

Each workcell needs local agent context:

- `MODULE_CONTRACT.md` or a centralized module contract that points to the
  workcell;
- `README.md` with purpose, surfaces, dependencies, invariants, and verification;
- `TODO.md` with current gaps, next tasks, known debt, and blocked work;
- proof commands or explicit missing-proof markers for critical promises.

Recommended README structure:

```markdown
# <workcell>

## Purpose
## Surfaces
## Dependencies
## Invariants
## Verification
## Notes
```

Recommended TODO structure:

```markdown
# <workcell> TODO

## Current
## Next
## Known Gaps
## Deferred
```

Keep local docs short. If a README needs a long design history, move durable
decisions into ADRs or split the workcell.

## Contract Fields

The compatibility fields remain:

- `module`;
- `level`;
- `surface`;
- `dependencies`;
- `consumers`;
- `invariants`;
- `verification`;
- `agent_policy`.

Workcell-aware contracts should also describe:

```yaml
workcell:
  type: leaf # project | composite | leaf
  parent: <parent-workcell-or-empty>
  children: []
  context_path: <relative path to README.md and TODO.md when module is logical>
  owns_paths:
    - <relative path>
  context_budget:
    max_files: 12
    max_source_lines: 1500
    max_contract_lines: 180
    max_readme_lines: 120
    max_todo_lines: 80
    max_surfaces: 8
    max_invariants: 8
  budget_exceptions:
    - metric: max_source_lines
      reason: Temporary migration workcell; split after the parser rewrite lands.
authority:
  write_policy: single_active_write_lease
  orchestrator: <owner or parent workcell>
  read_agents: many_allowed
  migration_lease_required:
    - cross-workcell write
    - public surface migration
```

Use `metric: context_budget` only for a broad temporary exception. Prefer a
specific metric such as `max_files`, `max_source_lines`, `max_contract_lines`,
`max_readme_lines`, `max_todo_lines`, `max_surfaces`, or `max_invariants`.
Exceptions should be rare and easy for an agent to understand.

## Decision Rules

- If the change is inside one leaf workcell, assign one write agent there.
- If the change spans child workcells, the nearest composite orchestrator
  decomposes it and delegates leaf-local writes.
- If the change cannot be decomposed cleanly, create a migration lease.
- If a workcell exceeds its context budget, split it or justify the exception.
- If a parent wants to edit child implementation directly, it is using the wrong
  authority level.
- If two write agents need the same workcell, serialize the work.

COAD parallelism comes from many small, independently owned workcells, not from
many agents editing the same boundary at once.
