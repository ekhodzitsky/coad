"""Extension layer for the COAD validator.

The standard (`coad_validator` core) checks the COAD-001..COAD-015 rules in
`STANDARD.md`. Extension submodules add optional checks that activate only
when the target repository contains the relevant evidence documents.

Today the only extension is :mod:`coad_validator.extensions.evidence`, which
re-exports task / proof / handoff / ledger / proof-artifact report builders
and their JSON-schema dependencies. The implementation still lives in the
top-level `coad_validator` package; this namespace exists so that callers
can opt in explicitly.
"""

from __future__ import annotations

from . import evidence

__all__ = ["evidence"]
