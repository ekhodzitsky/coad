# Module Contract

A Module Contract describes one workcell ownership boundary.

It is the base unit of COAD. Agents use it to understand what a workcell owns,
what promises must be preserved, what evidence protects those promises, and
when edits require escalation.

`MODULE_CONTRACT.md` is the compatibility filename. Conceptually, this is the
workcell contract.

## Required Fields

```yaml
schema_version: 1
kind: module_contract
module: billing
level: root
layer: domain
purpose: Calculate invoice totals and expose billing decisions to callers.
status: pilot
owners:
  - platform
workcell:
  type: leaf
  parent: commerce
  children: []
  owns_paths:
    - billing/
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
  orchestrator: commerce
  read_agents: many_allowed
  migration_lease_required:
    - cross-workcell write
    - public surface migration
surface:
  - name: InvoiceCalculator
    kind: service
    visibility: internal
    contract: Calculates deterministic invoice totals from line items and rates.
    proof:
      kind: unit-test
      target: billing.invoice_calculator.deterministic_totals
      command: test billing.invoice_calculator.deterministic_totals
dependencies:
  internal:
    - module: pricing
      scope: rate lookup only
      reason: Billing must use canonical customer rates.
  external:
    - name: decimal arithmetic library
      scope: money calculations
      reason: Floating point is not acceptable for currency.
consumers:
  - path: checkout
    uses:
      - InvoiceCalculator.calculate
invariants:
  - id: deterministic-total
    rule: Same input always produces the same total.
    proof:
      kind: unit-test
      target: billing.invoice_calculator.deterministic_totals
      command: test billing.invoice_calculator.deterministic_totals
verification:
  pre_change:
    - test billing
  full:
    - test all
    - lint all
agent_policy:
  allowed_mutations:
    - change internal implementation while preserving surface contracts
    - add focused tests for listed invariants
  forbidden_mutations:
    - remove listed surface without migration and consumer proof
    - add external dependency without decision record
  escalation:
    - invariant change
    - public surface removal
    - missing proof for critical behavior
```

## Semantics

- `module` is both the module identifier and, by default, the relative path to
  the module directory.
  Resolution tries the validation root first, then the directory containing the
  module contract. Absolute paths and `..` escapes are invalid.
- `workcell.context_path` may override that default when the workcell has a
  logical identifier but shares or centralizes its local agent context.
- `surface` lists promises, not every private function.
- `dependencies` must include reason and scope.
- `consumers` should be specific enough to test or inspect.
- `invariants` are rules that must remain true across changes.
- `proof` points to artifacts, not prose.
- `agent_policy` tells agents what they may do without guessing.
- `workcell` describes whether the contract is for a project, composite, or
  leaf workcell, plus parent/child relationships and context budgets.
- `workcell.budget_exceptions` records temporary, reasoned exceptions when a
  workcell exceeds its declared context budget.
- `authority` describes who may write, who may read, and when a migration lease
  is required.

## Workcell Authority

A leaf workcell has at most one active write agent. A composite workcell is
owned by a read-only orchestrator that delegates implementation writes to child
workcells.

Cross-workcell implementation changes require a migration lease approved by the
nearest common orchestrator.

## Agent Context Files

Every module contract must resolve to a real module directory. The directory
must contain:

- `README.md` - what the module owns, exposes, depends on, and promises;
- `TODO.md` - current gaps, planned work, and known follow-ups.

`AGENTS.md` is optional and should be added only when the module has rules that
differ from the repository default.

`coad check .` enforces the directory, `README.md`, `TODO.md`, and declared
context budget requirements.

## Agent Use

An agent changing this module should:

1. Read the frontmatter.
2. Identify affected surface, consumers, invariants, and proof.
3. Make the smallest change inside allowed mutations.
4. Update proof for changed behavior.
5. Update this contract if surface, dependencies, consumers, invariants, verification, or policy changed.

## Anti-Patterns

- Listing consumers as "various".
- Describing proof in prose without a target and command.
- Creating contracts for tiny implementation details.
- Creating a workcell so large that agents need broad repository searches for
  local changes.
- Treating the contract as documentation only.
- Letting multiple write agents edit the same leaf workcell at once.
- Introducing interfaces only because contracts exist.
