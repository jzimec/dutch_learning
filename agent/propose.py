#!/usr/bin/env python3
"""Supervised patch proposal runner. Requires OPENAI_API_KEY; never writes source."""
import difflib
import fnmatch
import json
import os
from pathlib import Path
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / "agent/runner-config.json").read_text())
tasks = json.loads((ROOT / "agent/tasks.json").read_text())["tasks"]
task = next((t for t in sorted(tasks,key=lambda t:t["priority"]) if t["status"] in ("todo","in_progress")),None)
if not task:
    raise SystemExit("No runnable tasks")
key = os.environ.get("OPENAI_API_KEY")
if not key:
    raise SystemExit("OPENAI_API_KEY missing: no model request performed")
# Never send repository secrets or oversized files to a model.
candidates = ["dutch-auth.js", "agent/rules.md"]
sources = {}
for name in candidates:
    if any(fnmatch.fnmatch(name,p) for p in cfg["protected_paths"]):
        continue
    if not any(fnmatch.fnmatch(name,p) for p in cfg["allowed_paths"]):
        continue
    p = ROOT / name
    if p.is_file() and p.stat().st_size < 40000:
        sources[name] = p.read_text(encoding="utf-8")
if not sources:
    raise SystemExit("No safe readable source files")
prompt = {
    "task": task,
    "rules": (ROOT/"agent/rules.md").read_text(encoding="utf-8"),
    "sources": sources,
    "output_format": {"path": "one existing allowed path", "content": "complete replacement UTF-8 file content"},
}
payload = {
    "model": os.environ.get("AGENT_MODEL", "gpt-5.1-codex-mini"),
    "instructions": "You are a supervised code assistant. Return ONLY a JSON object with path and content. Make the smallest safe change addressing the task. Never change security policies or credentials. If the task cannot be completed safely with supplied files, return {\"path\":\"\",\"content\":\"\"}.",
    "input": json.dumps(prompt,ensure_ascii=False),
    "max_output_tokens": 6000,
}
req = urllib.request.Request(
    "https://api.openai.com/v1/responses",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req,timeout=120) as response:
        answer=json.load(response)
except urllib.error.HTTPError as exc:
    raise SystemExit(f"Model request failed with HTTP {exc.code}") from None
output="".join(part.get("text","") for item in answer.get("output",[]) if item.get("type")=="message" for part in item.get("content",[]) if part.get("type")=="output_text")
try:
    proposal=json.loads(output)
except json.JSONDecodeError:
    raise SystemExit("Model output is not valid JSON") from None
name=proposal.get("path","")
new=proposal.get("content","")
if name not in sources or not isinstance(new,str) or not new or new==sources[name]:
    raise SystemExit("No safe applicable change proposed")
if len(new)>60000:
    raise SystemExit("Proposed file exceeds size limit")
patch="".join(difflib.unified_diff(sources[name].splitlines(True),new.splitlines(True),fromfile="a/"+name,tofile="b/"+name))
if not patch:
    raise SystemExit("Empty patch")
out=ROOT/"agent-proposal.patch"
out.write_text(patch,encoding="utf-8")
print(f"Proposed patch for {task['id']}: {name}; {len(patch)} bytes. NO SOURCE FILES MODIFIED.")
