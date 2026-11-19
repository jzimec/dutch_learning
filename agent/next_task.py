#!/usr/bin/env python3
"""Select next task using a validated persisted state snapshot, if available."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "tasks.json").read_text(encoding="utf-8"))
tasks = data["tasks"]
snapshot = ROOT / "runtime-state.json"
if snapshot.exists():
    state = json.loads(snapshot.read_text(encoding="utf-8"))
    if not isinstance(state, dict) or state.get("version") != 1 or not isinstance(state.get("tasks"), dict):
        raise SystemExit("Invalid persisted task state")
    known = {task["id"] for task in tasks}
    if set(state["tasks"]) - known:
        raise SystemExit("Persisted state refers to unknown task IDs")
    for task in tasks:
        override = state["tasks"].get(task["id"])
        if override is None:
            continue
        if not isinstance(override, dict) or override.get("status") not in ("todo","in_progress","blocked","done","unverified"):
            raise SystemExit("Invalid persisted task status")
        if override["status"] == "done" and not override.get("evidence"):
            raise SystemExit("Persisted completion lacks evidence")
        task["status"] = override["status"]
runnable = sorted((t for t in tasks if t["status"] in ("todo", "in_progress")),key=lambda t:(t["priority"],t["id"]))
stamp = datetime.now(timezone.utc).isoformat()
if not runnable:
    print(f"[{stamp}] No runnable tasks. Review blocked tasks.")
    sys.exit(0)
task = runnable[0]
print(f"[{stamp}] Next task: {task['id']} - {task['title']}")
for criterion in task["acceptance"]:
    print(f" - {criterion}")
print("Execution status: queued, not automatically implemented.")
