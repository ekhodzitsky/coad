"""Evidence-layer report builders for the COAD validator.

This subpackage is a namespace alias. The actual implementation lives in
the top-level :mod:`coad_validator` package. Importing from here documents
that a caller is opting into the optional evidence-trail checks
(task / proof / handoff / ledger / proof-artifact integrity, methodology
loop aggregation, contract update integrity) instead of the standard's
core rules.

The validator activates these checks automatically when the target
repository contains any of:

- ``goal_contract``, ``task_contract``, ``proof_contract``,
  ``handoff_contract``, ``review_contract``, or ``integration_contract``
  Markdown frontmatter;
- ``HANDOFF.md`` or ``EXECUTION_LEDGER.json`` at the repository root.

Schemas for these contracts live in ``schema/extensions/``.
"""

from __future__ import annotations

from coad_validator.contract_update_integrity import build_contract_update_integrity_report
from coad_validator.handoff_integrity import build_handoff_integrity_report
from coad_validator.ledger import build_ledger_report
from coad_validator.ledger_handoff_integrity import build_ledger_handoff_integrity_report
from coad_validator.methodology_loop import build_methodology_loop_report
from coad_validator.proof_artifact_integrity import build_proof_artifact_integrity_report
from coad_validator.proof_matrix import build_proof_matrix
from coad_validator.proof_result_integrity import build_proof_result_integrity_report
from coad_validator.task_scope_integrity import build_task_scope_integrity_report

__all__ = [
    "build_contract_update_integrity_report",
    "build_handoff_integrity_report",
    "build_ledger_handoff_integrity_report",
    "build_ledger_report",
    "build_methodology_loop_report",
    "build_proof_artifact_integrity_report",
    "build_proof_matrix",
    "build_proof_result_integrity_report",
    "build_task_scope_integrity_report",
]
