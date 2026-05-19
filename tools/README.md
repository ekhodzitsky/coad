# Tools

This directory is reserved for reference tooling.

Public command:

- `coad check .` - single-command boundary and evidence check for agent dev flow.

The validator still has internal report builders for tests and repository
self-checks, but they are not exposed as user-facing CLI commands. The intended
integration surface for another repository or agent is only `coad check .`.

COAD Core should remain useful without tools, but tools should make contract
use repeatable and hard to fake when agents or CI need evidence.
