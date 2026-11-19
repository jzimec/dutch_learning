#!/usr/bin/env python3
"""Load task status from a GitHub Issue body; fail closed on malformed state."""
import json
import os
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parent
repo=os.environ.get("GITHUB_REPOSITORY","")
if not repo:
    raise SystemExit("GITHUB_REPOSITORY missing")
title="Dutch Learning | Agent task state"
lookup=subprocess.run(["gh","issue","list","--repo",repo,"--state","open","--limit","100","--json","number,title"],capture_output=True,text=True,check=True)
matches=[x for x in json.loads(lookup.stdout) if x["title"]==title]
if not matches:
    print("No persisted task state issue; using version-controlled task defaults.")
    raise SystemExit(0)
if len(matches)!=1:
    raise SystemExit("Ambiguous task state issues")
number=str(matches[0]["number"])
body=subprocess.run(["gh","issue","view",number,"--repo",repo,"--json","body","--jq",".body"],capture_output=True,text=True,check=True).stdout
marker="<!-- dutch-learning-agent-state-v1 -->"
if marker not in body:
    raise SystemExit("Task state issue has no valid marker")
payload=body.split(marker,1)[1].strip()
try:
    state=json.loads(payload)
except json.JSONDecodeError as exc:
    raise SystemExit(f"Invalid task state JSON: {exc}") from None
if state.get("version")!=1 or not isinstance(state.get("tasks"),dict):
    raise SystemExit("Invalid task state schema")
known={t["id"] for t in json.loads((root/"tasks.json").read_text(encoding="utf-8"))["tasks"]}
if set(state["tasks"])-known:
    raise SystemExit("Task state contains unknown task IDs")
for task_id,entry in state["tasks"].items():
    if not isinstance(entry,dict) or entry.get("status") not in {"todo","in_progress","blocked","done","unverified"}:
        raise SystemExit(f"Invalid status for {task_id}")
    if entry["status"]=="done" and not entry.get("evidence"):
        raise SystemExit(f"Missing completion evidence for {task_id}")
(root/"runtime-state.json").write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(f"Loaded persisted task state from issue #{number}")
