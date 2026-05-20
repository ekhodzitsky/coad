# COAD Specification

This document is the body of the methodology — the part that turns the
ten [principles](PRINCIPLES.md) into something a team can apply. It is
prose, not RFC 2119. Every rule below is a recommendation; the team
that owns a module decides how strictly to follow it.

Read this once. Skim later. The [agent onboarding](AGENT_ONBOARDING.md)
page references terms from section 1.

## 1. Vocabulary

**Module.** A unit of code with one owner, one purpose, and one
boundary. Usually a directory; sometimes a package; sometimes a service.
A module is not its directory — it is the boundary around its
responsibility.

**Workcell.** The smallest independently editable unit of agent work.
For small projects, a workcell is the same as a module. For larger
projects, a module can be a composite workcell whose children (sub-
modules) are the actual leaf workcells. The normal write unit is a leaf
workcell.

**Module contract.** A short Markdown file (`MODULE_CONTRACT.md`)
beside the module that names its purpose, public surface, internal
dependencies, consumers, invariants, and proof commands. It is what an
agent reads before editing.

**Surface.** A function, type, schema, event, command, protocol, or
data shape that other modules or external systems rely on. A surface
is **public** when something outside the module depends on it,
**internal** when only files inside the module reference it.

**Consumer.** A module, workflow, or external system that depends on
this module's surface. A consumer is named by path or service id, plus
the specific surfaces it uses.

**Invariant.** A promise the module keeps across changes. Example: «a
`CheckoutDecision` never carries a negative total». Invariants are the
things agents must not silently break.

**Proof.** A repeatable artifact that demonstrates a surface or
invariant still holds. Examples: a passing unit test, a schema check, a
golden-file comparison, a static-check command, a smoke run, a
benchmark threshold, an explicit human review note, or an explicit
declaration of missing proof debt. Proof is **named** (so it can be
re-run) and **structured** (so it can be reviewed), not prose.

**Dependency.** An internal module or external system this module
needs. Each dependency carries a reason — the human-readable answer to
«why does this module touch that one?»

**Drift.** A state where the code no longer matches the module contract.
Drift exists when the surface, dependencies, consumers, invariants, or
verification commands change but the contract does not. Drift is a
bug.

**Lease.** A visible declaration that an agent is currently writing
inside a workcell. The value is in being visible to other agents and
humans; how the team makes leases visible is up to them (a file, a
ticket field, a chat channel — anything readable).

**Handoff.** The artifact a worker leaves behind when its task exits.
Lists changed files, surfaces touched, invariants checked, proof run,
known gaps, and follow-up tasks. A handoff is durable — it must be
useful without the sender's chat history.

**Read scope, write scope.** The set of files an agent will read for
context, and the smaller set it will modify. Write scope should stay
inside the workcell's owned paths.

## 2. The methodology in one page

A COAD-native repository has a tree of modules, each with its own
`MODULE_CONTRACT.md`, `README.md`, and `TODO.md`. When an agent gets a
task, it:

1. Reads the relevant module contract.
2. Identifies surfaces, invariants, and proof commands.
3. Locks read scope and write scope before editing.
4. Edits the smallest change that satisfies the task.
5. Runs the proof commands.
6. Updates the contract if surface, dependencies, consumers,
   invariants, or verification changed.
7. Writes a handoff with the diff, the proof results, and known gaps.

That is the loop. Everything in this document — vocabulary, examples,
limitations — exists to make this loop applicable to a real codebase.

## 3. Module contract

A module contract answers six questions about the module:

| Question                     | Field          |
| ---------------------------- | -------------- |
| What does this module own?   | `purpose`      |
| What does it expose?         | `surface`      |
| What does it need?           | `dependencies` |
| Who depends on it?           | `consumers`    |
| What must stay true?         | `invariants`   |
| How do we know it works?     | `proof`        |

There is no fixed format. The YAML-frontmatter shape in
`AGENT_ONBOARDING.md` is one option; a plain Markdown contract with
headed sections works equally well. Pick the form that survives review
in your team.

A good module contract is short enough to read in two minutes. If a
contract takes longer than that to read, the module is probably too
large and should be split into smaller workcells.

## 4. Lifecycle

The COAD agent lifecycle has six phases. Each phase has one obligation
and one signal that it is done.

| Phase           | Obligation                                                | Done when                                 |
| --------------- | --------------------------------------------------------- | ----------------------------------------- |
| Orient          | Read contract, README, TODO. Identify boundary.           | Agent can answer the six contract questions. |
| Scope           | Lock read scope and write scope.                          | Both scopes are written down before editing. |
| Edit            | Make the smallest change that satisfies the task.         | Diff is bounded by write scope.           |
| Prove           | Run the relevant proof commands.                          | Proof passes, or missing proof is declared. |
| Update knowledge| Update contract, README, TODO if context changed.         | No drift remains, or remaining drift is named. |
| Handoff         | Produce a durable handoff artifact.                       | Next agent or human can continue without chat. |

A phase may be skipped only when its obligation is empty. A
documentation-only edit usually skips Prove; a refactor that preserves
all surfaces usually skips Update Knowledge.

## 5. Drift and contract updates

Drift exists when:

- code exposes a surface not listed in the contract;
- a listed surface no longer exists;
- a dependency is used but not declared, or declared but unused;
- a known consumer is missing from the list;
- an invariant is violated, weakened, or no longer has proof;
- a proof command no longer runs.

Detecting drift relies on code review, periodic audits, and the
«before editing, read the contract» habit. The methodology itself does
not describe how to detect drift; that belongs to the team's review
process.

Resolving drift has two outcomes. Either the code is the source of
truth and the contract changes, or the contract is the source of truth
and the code reverts. The team owning the module decides which.

## 6. Three worked examples

### 6.1. Bug fix inside one module

Task: «In `src/checkout/`, `CheckoutDecision` returns a negative total
when discounts exceed the cart subtotal.»

- **Orient.** Agent reads `src/checkout/MODULE_CONTRACT.md`. The
  contract declares the invariant `no-negative-total` with proof
  `test checkout.rejects_negative_total`.
- **Scope.** Read scope: `src/checkout/`. Write scope: same.
- **Edit.** Add a guard in `CheckoutService` that rejects carts whose
  computed total is negative.
- **Prove.** Run `test checkout.rejects_negative_total`. It passes.
- **Update knowledge.** No surface change, no new dependency. Skip.
- **Handoff.** «Fixed negative-total bug. Files changed:
  `src/checkout/service.py`, `tests/test_checkout.py`. Invariant
  `no-negative-total` now enforced. No consumer impact.»

### 6.2. Public surface change with consumer migration

Task: «`CheckoutDecision.total` is currently a `float`; switch it to a
typed `Money` value object.»

- **Orient.** Contract lists two consumers: `payment`, `fulfillment`.
  The surface `CheckoutDecision` is public. The invariant says nothing
  about `total`'s type, only its sign.
- **Scope.** Read scope: `src/checkout/`, `src/payment/`,
  `src/fulfillment/`. Write scope: all three. The change touches the
  shared invariant boundary, so it is not a leaf-workcell edit.
- **Edit.** Introduce `Money`. Update `CheckoutDecision`. Update
  `payment` and `fulfillment` to read `total.amount` and
  `total.currency`. Update the JSON schema for `CheckoutDecision`.
- **Prove.** Run proof for all three modules, plus contract test for
  the `CheckoutDecision` schema.
- **Update knowledge.** `src/checkout/MODULE_CONTRACT.md`: surface
  signature changed. `src/payment/MODULE_CONTRACT.md` and
  `src/fulfillment/MODULE_CONTRACT.md`: dependency descriptions updated
  to mention `Money`. Add ADR if the team uses them.
- **Handoff.** Includes diff, the three contracts updated, proof for
  each module, plus a follow-up note for downstream services that read
  the JSON.

### 6.3. Parallel work across two leaf workcells

Two agents, two independent tasks, same release.

- Agent A: «In `src/checkout/`, log every rejected cart with reason.»
- Agent B: «In `src/billing/`, add quarterly invoice rollup.»

- **Orient.** Both agents read their respective module contracts.
  Checkout consumers list does not include billing. Billing consumers
  list does not include checkout. The surfaces are disjoint.
- **Scope.** Agent A: `src/checkout/`. Agent B: `src/billing/`. No
  overlap.
- **Lease (advisory).** If the repo tracks leases, Agent A writes a
  lease on `src/checkout/`, Agent B on `src/billing/`. If not, the
  agents announce their workcells in chat or in a tracker.
- **Edit, prove, update, handoff.** Independent.

The parallelism is safe because the contracts are disjoint, not
because the files differ. The contract check is what makes
parallelism safe — file paths alone are not enough.

## 7. When to use COAD

COAD pays off when:

- coding agents (LLM-driven or otherwise) edit a non-trivial repository;
- ownership boundaries are not obvious from the directory tree;
- changes lose context across handoffs between people or sessions;
- there is value in being able to say «this change touches that
  surface» before approving a merge;
- multiple workers need to make progress in parallel without breaking
  each other.

## 8. When NOT to use COAD

Skip COAD when:

- the project has a single author who keeps the whole map in their head;
- the repository is a throwaway prototype;
- the team already has strong CODEOWNERS, design docs, and tests, and
  feels no pain from agent handoffs;
- every change touches the whole codebase and there are no stable
  internal boundaries to declare;
- the cost of writing module contracts would exceed the cost of
  re-reading the code each time.

COAD is overhead. Without the pain it solves, the overhead is loss.

## 9. Integration with other practices

**Code review.** COAD adds context *before* review. The reviewer reads
the contract, sees what the change is supposed to preserve, and only
then reads the diff. Reviews become contract-anchored: «did this
change respect the invariants?» replaces «does this look right?»

**CODEOWNERS.** COAD complements CODEOWNERS. CODEOWNERS says «who
approves»; the module contract says «what they should look for». A
mature repo references CODEOWNERS from the contract's owners list.

**Architecture Decision Records (ADR).** ADRs document horizontal
decisions («we use Postgres»). Module contracts document vertical
ownership («this module owns checkout decisions»). They do not
overlap; both are useful.

**Design docs.** Design docs are forward-looking; module contracts
describe the current state. When a design doc is approved and shipped,
its commitments move into the module contract.

**Tests.** Tests prove invariants. Module contracts name the
invariants and point at the tests. The contract makes tests
discoverable; the tests make the contract enforceable.

**Other agent-development methods (Spec Kit, BMAD, Agent OS,
Repomix).** Those describe workflows, runtimes, or context packaging.
COAD describes the **shape of the repository** the agent enters. They
compose: pick a workflow framework, use COAD to make the repo
agent-navigable for it.

## 10. Limitations

- COAD does not enforce anything. Contracts drift if no one looks
  after them; that is review's job, not the methodology's.
- A contract is only useful if someone reads it. If the team's habit
  is «edit first, read later», COAD has zero effect.
- Module contracts can become aspirational. A contract that lists
  consumers as «unknown» is worse than no contract — it gives false
  confidence.
- COAD scales by adding modules, not by adding contract complexity. A
  500-line `MODULE_CONTRACT.md` is a sign the module is too big.
- Proof discipline is the hardest part. Most teams adopt COAD's
  vocabulary fast but slip on proof. The methodology is honest about
  this in principle 6 («Proof Is Structured»); the practice is harder
  than the principle.
- The methodology assumes the team agrees on what a «module» is.
  Re-organising the codebase into modules is the part COAD does not
  help with.

## 11. Maturity

A team can adopt COAD incrementally:

1. **One contract.** Pick the module that hurts most. Write its
   contract. Stop there. See if the team uses it.
2. **Three contracts.** If the first one survived, write contracts for
   two adjacent modules. Now the consumer list of the first contract
   points at real files, not «unknown».
3. **All public modules.** Cover every module with a non-trivial
   public surface.
4. **Drift discipline.** Add code-review checklist: «did the contract
   change?» Optionally automate it.
5. **Parallel work.** When two agents work concurrently, declare
   leases. Optionally automate conflict detection.

A team that gets stuck at step 2 has learned something useful: COAD
does not match their pain.
