#!/usr/bin/env python3
"""Safely persist a task transition to the dedicated GitHub state issue."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from state import transition

ROOT=Path(__file__).resolve().parent
MARKER="<!-- dutch-learning-agent-state-v1 -->"
TITLE="Dutch Learning | Agent task state"

def gh(*args):
    result=subprocess.run(["gh",*args],capture_output=True,text=True,check=True)
    return result.stdout.strip()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--task",required=True)
    parser.add_argument("--status",required=True,choices=["todo","in_progress","blocked","unverified","done"])
    parser.add_argument("--evidence",default="")
    args=parser.parse_args()
    repo=os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        raise SystemExit("GITHUB_REPOSITORY missing")
    queue=json.loads((ROOT/"tasks.json").read_text(encoding="utf-8"))["tasks"]
    task=next((t for t in queue if t["id"]==args.task),None)
    if task is None:
        raise SystemExit("Unknown task ID")
    matches=[x for x in json.loads(gh("issue","list","--repo",repo,"--state","open","--limit","100","--json","number,title")) if x["title"]==TITLE]
    if len(matches)!=1:
        raise SystemExit("Expected exactly one open state issue")
    number=str(matches[0]["number"])
    body=gh("issue","view",number,"--repo",repo,"--json","body","--jq",".body")
    if MARKER not in body:
        raise SystemExit("Missing state marker")
    state=json.loads(body.split(MARKER,1)[1].strip())
    if state.get("version")!=1 or not isinstance(state.get("tasks"),dict):
        raise SystemExit("Invalid state schema")
    existing=state["tasks"].get(args.task,{"status":task["status"]})
    updated=transition(existing,args.status,args.evidence or None)
    state["tasks"][args.task]=updated
    replacement="Persistent Dutch Learning agent task state.\n\n"+MARKER+"\n"+json.dumps(state,indent=2,ensure_ascii=False)+"\n"
    # GitHub CLI accepts --body, avoiding shell interpolation of JSON.
    gh("issue","edit",number,"--repo",repo,"--body",replacement)
    print(f"Updated {args.task} to {args.status} in issue #{number}")

if __name__=="__main__":
    main()
