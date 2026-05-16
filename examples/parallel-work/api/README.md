# parallel-work/api

Purpose: represent an API leaf workcell that can be edited by one write agent.

Owned files are under `api/`. Documentation work in `docs/` is a separate leaf
workcell and can proceed in parallel.

Proof:

```bash
coad check examples/parallel-work
```
