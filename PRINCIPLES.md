# Principles

## 1. Contracts Beat Memory

Agent handoffs must not depend on chat history. The durable source of truth is the contract graph plus proof artifacts.

## 2. Modules Are Ownership Boundaries

A module is not just a directory. It is a boundary with purpose, surface, dependencies, consumers, invariants, and proof.

## 3. Agents Execute, Contracts Accept

Agents may propose that work is done. Completion is accepted only when the relevant proof and review contracts pass.

## 4. Context Must Be Bounded

Give an agent the smallest context pack that lets it preserve the contract. Too much context is noise; too little context is risk.

## 5. Parallelism Requires Non-Overlapping Contracts

Two agents may work in parallel only when their write scopes and contract surfaces do not conflict, or when dependencies serialize the work.

## 6. Proof Is Structured

Proof is not prose. It is a named, repeatable artifact: test, schema check, golden file, static check, smoke run, benchmark, review result, or explicit missing proof debt.

## 7. Drift Is A Bug

If code changes the surface, dependency graph, consumers, invariants, or verification commands, the relevant contract must change too.

## 8. Review Findings Become Work

A blocking review finding is not a comment to remember. It becomes a task contract with owner, scope, required proof, and terminal state.

## 9. Escalation Is A Valid Outcome

When proof cannot be defined, safety assumptions change, or a human decision is needed, the correct result is blocked with evidence.

## 10. Ceremony Must Buy Safety

A contract is justified only when it makes change safer, faster, or easier to review. Do not create contracts for tiny implementation details.
