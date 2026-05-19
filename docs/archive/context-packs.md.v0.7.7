# Context Packs

A context pack is the bounded input an orchestrator gives to an agent for one
task.

It exists to prevent two common failures:

- agents reading a whole repository and losing the important contract details;
- agents reading too little and missing consumers, proof, or integration gates.

## Contents

A COAD context pack SHOULD include:

- the goal contract that owns the task;
- the task contract;
- module contracts listed by the task;
- workcell authority and context-budget notes from those module contracts;
- proof contracts required by the task;
- review contracts targeting the task;
- handoff contracts for the task when they exist;
- the integration contract that will accept or reject the task output.

## Exclusions

A context pack SHOULD NOT include unrelated modules, unrelated tasks, stale chat
history, broad repository dumps, or child implementation files when the assigned
agent only has composite read-only orchestration authority.

## Reference Builder

The reference validator package keeps an internal context pack builder for tests
and future orchestrators. It validates the contract graph before producing
output. If the graph is invalid, packing fails instead of handing an agent
incomplete context.

## Current Output

The first reference implementation emits JSON. Each included contract contains:

- `id`;
- `kind`;
- `path`;
- parsed frontmatter `data`.

Future implementations may add Markdown rendering, source snippets, proof
artifacts, token budgets, or agent-specific prompt sections.

## Acceptance Rule

An orchestrator MUST NOT treat a context pack as proof. A context pack is input
for execution; proof and review contracts still decide readiness.
