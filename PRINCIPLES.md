# Principles

Each principle has one rule. The pointer (`→ SPEC ...`) names where the
principle is unpacked with definitions or worked through with examples.

## 1. Contracts Beat Memory

Agent handoffs must not depend on chat history. The durable source of
truth is the contract graph plus proof artifacts.
→ SPEC §1 (handoff, module contract), §6.2 (consumer migration handoff).

## 2. Modules Are Ownership Boundaries

A module is not just a directory. It is a boundary with purpose,
surface, dependencies, consumers, invariants, and proof.
→ SPEC §1 (module, surface, invariant, consumer), §3 (reference contract).

## 3. Agents Execute, Contracts Accept

Agents may propose that work is done. Completion is accepted only when
the relevant proof and review contracts pass.
→ SPEC §4 phase «Prove», §6.1 (negative-total fix).

## 4. Context Must Be Bounded

Give an agent the smallest context pack that lets it preserve the
contract. Too much context is noise; too little context is risk.
→ SPEC §1 (read scope, write scope), §4 phase «Scope».

## 5. Parallelism Requires Non-Overlapping Contracts

Two agents may work in parallel only when their write scopes and
contract surfaces do not conflict, or when dependencies serialize the
work.
→ SPEC §1 (lease), §6.3 (parallel leaf workcells).

## 6. Proof Is Structured

Proof is not prose. It is a named, repeatable artifact: test, schema
check, golden file, static check, smoke run, benchmark, review result,
or explicit missing proof debt.
→ SPEC §1 (proof), §3 (proof commands in reference contract).

## 7. Drift Is A Bug

If code changes the surface, dependency graph, consumers, invariants,
or verification commands, the relevant contract must change too.
→ SPEC §5 (drift definition and resolution).

## 8. Review Findings Become Work

A blocking review finding is not a comment to remember. It becomes a
follow-up task with owner, scope, required proof, and terminal state.
→ SPEC §4 phase «Handoff» (follow-up tasks), §10 (limitations on review).

## 9. Escalation Is A Valid Outcome

When proof cannot be defined, safety assumptions change, or a human
decision is needed, the correct result is blocked with evidence.
→ SPEC §4 phase «Prove» («missing proof is declared»).

## 10. Ceremony Must Buy Safety

A contract is justified only when it makes change safer, faster, or
easier to review. Do not create contracts for tiny implementation
details.
→ SPEC §8 (when NOT to use COAD), §10 (limitations), §11 (maturity).
