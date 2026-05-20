# Agent Onboarding

You are a coding agent. A human asked you to adopt COAD in their
repository. This file is your single-page instruction.

COAD is a methodology — prose, not code. Adoption means writing four
files; correctness comes from judgment and review.

## What to do

1. Read [PRINCIPLES.md](PRINCIPLES.md) and the vocabulary section of
   [SPEC.md](SPEC.md). The work has to be consistent with those ten
   principles and use the terms correctly.
2. Inspect the target repository. Pick one real module/workcell with
   public API, fragile invariants, or frequent edits.
3. Update target `AGENTS.md` with the snippet below.
4. Add one root `MODULE_CONTRACT.md` (template below).
5. Ensure the workcell directory has `README.md` and `TODO.md` with one
   line of real content each.
6. Hand off: list changed files, the chosen workcell, what you covered,
   and the gaps you left.

Skip anything that does not match the user's repository. COAD is
guidance — not RFC 2119.

## AGENTS.md snippet

```text
Use COAD methodology. https://github.com/ekhodzitsky/coad
Before editing, read the relevant MODULE_CONTRACT.md and the
workcell README.md + TODO.md. Treat handoff as a durable artifact,
not a chat summary. One leaf workcell, one active write agent.
```

## MODULE_CONTRACT.md template

A starter shape. Adapt the fields and the format (YAML frontmatter,
plain Markdown sections, table — whatever the team will read).

```yaml
---
module: checkout
purpose: Convert validated carts into payment-ready checkout decisions.
owns_paths:
  - src/checkout/
surface:
  - name: CheckoutDecision
    visibility: public
    contract: Stable read model consumed by payment and fulfillment.
    proof: test schemas/checkout-decision.schema.json
consumers:
  - payment
  - fulfillment
invariants:
  - id: no-negative-total
    rule: CheckoutDecision never carries a negative total.
    proof: test checkout.rejects_negative_total
---

# checkout

Application-level checkout decisions. Does not own pricing rules,
payment capture, or fulfillment side effects.
```

## Done when

The target repo has `AGENTS.md` pointing at COAD; `MODULE_CONTRACT.md`
exists for one real module; that module has real `README.md` +
`TODO.md`; the human can read the contract and trust your next edit.
