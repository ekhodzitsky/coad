from __future__ import annotations

from pathlib import Path
from typing import Any

from .graph_index import ContractIndex
from .model import ContractDocument
from .report import versioned_report
from .validate import validate_path


def build_proof_matrix(root: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    report = validate_path(root, schema_dir=schema_dir)
    if not report.ok:
        return versioned_report(
            {
                "ok": False,
                "ready": False,
                "status": "invalid",
                "contracts": len(report.documents),
                "issues": [issue.to_json(report.root) for issue in report.issues],
            }
        )

    index = ContractIndex.from_documents(report.documents)
    goals = [
        _goal_matrix(goal, index, report.root)
        for goal in index.goals()
    ]
    ready = bool(goals) and all(goal["ready"] for goal in goals)
    return versioned_report(
        {
            "ok": True,
            "ready": ready,
            "status": "ready" if ready else "not_ready",
            "contracts": len(report.documents),
            "goals": goals,
        }
    )


def _goal_matrix(
    goal: ContractDocument,
    index: ContractIndex,
    root: Path,
) -> dict[str, Any]:
    tasks = [_task_matrix(task, index, root) for task in index.goal_tasks(goal)]
    blockers = [blocker for task in tasks for blocker in task["blockers"]]
    ready = not blockers
    return {
        "goal_id": goal.identifier,
        "path": _relative_path(goal, root),
        "ready": ready,
        "status": "ready" if ready else "not_ready",
        "blockers": blockers,
        "tasks": tasks,
    }


def _task_matrix(
    task: ContractDocument,
    index: ContractIndex,
    root: Path,
) -> dict[str, Any]:
    task_id = task.identifier
    handoff = index.handoff_for_task(task_id)
    proofs = [
        _proof_entry(task, required, handoff, index, root)
        for required in _required_task_proofs(task)
    ]
    blockers = [
        _blocker(task, root, f"task {task_id} missing passing evidence for proof command: {proof['command']}")
        for proof in proofs
        if proof["status"] != "pass"
    ]
    ready = not blockers
    return {
        "task_id": task_id,
        "path": _relative_path(task, root),
        "change_class": _string_value(task.data.get("change_class"), "unknown"),
        "ready": ready,
        "status": "ready" if ready else "not_ready",
        "blockers": blockers,
        "proofs": proofs,
    }


def _proof_entry(
    task: ContractDocument,
    required: dict[str, Any],
    handoff: ContractDocument | None,
    index: ContractIndex,
    root: Path,
) -> dict[str, Any]:
    proof_id = _string_value(required.get("proof_id"), "")
    command = _string_value(required.get("command"), "")
    proof_contract = index.proof(proof_id)
    evidence = _handoff_evidence(command, handoff, root)
    status = "pass" if evidence is not None and evidence["status"] == "pass" else "missing_evidence"
    return {
        "proof_id": proof_id,
        "command": command,
        "kind": _string_value(required.get("kind"), "unknown"),
        "target": _string_value(required.get("target"), ""),
        "proof_contract": _contract_ref(proof_contract, root),
        "evidence": evidence,
        "status": status,
    }


def _handoff_evidence(
    command: str,
    handoff: ContractDocument | None,
    root: Path,
) -> dict[str, str] | None:
    if handoff is None:
        return None
    proof_results = handoff.data.get("proof_results")
    if not isinstance(proof_results, list):
        return None
    for item in proof_results:
        if not isinstance(item, dict):
            continue
        if item.get("command") != command:
            continue
        status = item.get("status")
        return {
            "status": status if isinstance(status, str) else "unknown",
            "source": _relative_path(handoff, root),
        }
    return None


def _required_task_proofs(task: ContractDocument) -> list[dict[str, Any]]:
    proof = task.data.get("proof")
    if not isinstance(proof, dict):
        return []
    required = proof.get("required")
    if not isinstance(required, list):
        return []
    return [item for item in required if isinstance(item, dict)]


def _contract_ref(document: ContractDocument | None, root: Path) -> dict[str, str] | None:
    if document is None:
        return None
    return {
        "id": document.identifier,
        "path": _relative_path(document, root),
    }


def _blocker(document: ContractDocument, root: Path, message: str) -> dict[str, str]:
    return {
        "kind": document.kind,
        "id": document.identifier,
        "path": _relative_path(document, root),
        "message": message,
    }


def _relative_path(document: ContractDocument, root: Path) -> str:
    try:
        return str(document.path.relative_to(root))
    except ValueError:
        return str(document.path)


def _string_value(value: object, fallback: str) -> str:
    return value if isinstance(value, str) and value else fallback
