#!/usr/bin/env python3
"""Deterministic task selector for Dutch Learning. No AI or code writes."""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "tasks.json").read_text(encoding="utf-8"))
tasks = sorted(
    (t for t in data["tasks"] if t["status"] in ("todo", "in_progress")),
    key=lambda t: (t["priority"], t["id"]),
)
stamp = datetime.now(timezone.utc).isoformat()
if not tasks:
    print(f"[{stamp}] No runnable tasks. Blocked tasks need human review.")
else:
    task = tasks[0]
    print(f"[{stamp}] Next task: {task['id']} - {task['title']}")
    print("Acceptance criteria:")
    for criterion in task["acceptance"]:
        print(f" - {criterion}")
    print("Execution status: queued, not automatically implemented.")
