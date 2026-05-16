# Parallel Work Example Agent Guide

Use COAD for coordinated agent development.

Before editing:

1. Read the relevant `MODULE_CONTRACT.md`.
2. Read the workcell `README.md` and `TODO.md`.
3. Declare or verify the active lease in `.coad/leases.yml`.
4. Run the workcell proof command.
5. Run `coad check .`.

Keep work inside the declared workcell ownership. Maintain module contracts
when ownership, surfaces, invariants, or verification change.
