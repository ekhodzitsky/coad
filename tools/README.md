# Tools

This directory is reserved for reference tooling.

Current tools:

- `coad-validate` - validates contract schemas and graph references.
- `coad-pack` - emits bounded task context packs for orchestrators and agents.
- `coad-status` - reports whether a contract graph is ready or blocked.
- `coad-proof-matrix` - reports required proof commands and handoff evidence.
- `coad-graph` - exports contract nodes and typed graph edges.
- `coad-schedule` - builds dependency/write-scope execution waves for tasks.
- `coad-ledger` - audits durable execution ledgers against task proof contracts.
- `coad-profile` - reports declared COAD conformance profile status.
- `coad-drift` - checks whether tool docs, schemas, and CI are aligned.

Planned tools:

- visual graph renderer

The methodology should remain useful without tools, but tools should make contract use repeatable and hard to fake.
