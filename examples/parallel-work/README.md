# parallel-work

Purpose: show how a composite orchestrator can coordinate two independent leaf
workcells with active leases.

The root workcell is read-only orchestration. Implementation writes happen in
`api/` and `docs/`, each with its own leaf write lease in `.coad/leases.yml`.

Proof:

```bash
coad check examples/parallel-work
```
