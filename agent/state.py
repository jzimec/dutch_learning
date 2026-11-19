"""Deterministic agent state transitions. No repository writes."""
from datetime import datetime, timezone

VALID = {"todo", "in_progress", "blocked", "done", "unverified"}
TRANSITIONS = {
    "todo": {"in_progress", "blocked"},
    "in_progress": {"blocked", "unverified", "done"},
    "unverified": {"in_progress", "blocked", "done"},
    "blocked": {"todo"},
    "done": set(),
}


def transition(task, new_status, evidence=None):
    current = task["status"]
    if current not in VALID or new_status not in TRANSITIONS[current]:
        raise ValueError(f"Invalid transition {current} -> {new_status}")
    if new_status == "done" and not evidence:
        raise ValueError("Completion requires test evidence")
    updated = dict(task)
    updated["status"] = new_status
    updated["updated_at"] = datetime.now(timezone.utc).isoformat()
    if evidence:
        updated["evidence"] = evidence
    return updated
