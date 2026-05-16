# Module Contract

A Module Contract describes one ownership boundary.

It is the base unit of COAD. Agents use it to understand what a module owns, what promises must be preserved, what evidence protects those promises, and when edits require escalation.

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
- `surface` lists promises, not every private function.
- `dependencies` must include reason and scope.
- `consumers` should be specific enough to test or inspect.
- `invariants` are rules that must remain true across changes.
- `proof` points to artifacts, not prose.
- `agent_policy` tells agents what they may do without guessing.

## Agent Context Files

Every module contract must resolve to a real module directory. The directory
must contain:

- `README.md` - what the module owns, exposes, depends on, and promises;
- `TODO.md` - current gaps, planned work, and known follow-ups.

`AGENTS.md` is optional and should be added only when the module has rules that
differ from the repository default.

`coad check .` enforces the directory, `README.md`, and `TODO.md` requirements.

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
- Treating the contract as documentation only.
- Introducing interfaces only because contracts exist.
