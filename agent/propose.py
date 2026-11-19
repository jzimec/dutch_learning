#!/usr/bin/env python3
"""Supervised patch proposal runner. Requires OPENAI_API_KEY; never writes source."""
import difflib
import fnmatch
import json
import os
from pathlib import Path
from validate_proposal import validate_proposal
from response_parser import extract_proposal
import urllib.request
import urllib.error
import ast

ROOT = Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / "agent/runner-config.json").read_text())
tasks = json.loads((ROOT / "agent/tasks.json").read_text())["tasks"]
task = next((t for t in sorted(tasks,key=lambda t:t["priority"]) if t["status"] in ("todo","in_progress")),None)
if not task:
    raise SystemExit("No runnable tasks")
fixture_path = os.environ.get("AGENT_RESPONSE_FIXTURE")
key = os.environ.get("OPENAI_API_KEY")
if not key and not fixture_path:
    raise SystemExit("OPENAI_API_KEY missing: no model request performed")
if task["id"] != "AUTH-01":
    raise SystemExit(f"Task {task['id']} requires additional scoped sources; refusing unrelated changes")
# Never send repository secrets or oversized files to a model.
candidates = ["dutch-auth.js"]
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
if cfg["mode"] != "supervised" or cfg["auto_push"] or cfg["auto_merge"]:
    raise SystemExit("Unsafe runner configuration")
prompt = {
    "task": task,
    "rules": (ROOT/"agent/rules.md").read_text(encoding="utf-8"),
    "sources": sources,
    "output_format": {"path": "one existing allowed path", "content": "complete replacement UTF-8 file content"},
}
payload = {
    "model": (os.environ.get("AGENT_MODEL") or "gpt-4.1-mini"),
    "instructions": "You are a supervised code assistant. Return ONLY a JSON object with path and content. Make the smallest safe change addressing the task. Never change security policies or credentials. If the task cannot be completed safely with supplied files, return {\"path\":\"\",\"content\":\"\"}.",
    "input": json.dumps(prompt,ensure_ascii=False),
    "max_output_tokens": 12000,
}
if fixture_path:
    # Offline test fixture only. Do not permit fixture mode in GitHub Actions.
    if os.environ.get("GITHUB_ACTIONS") == "true":
        raise SystemExit("Fixture mode forbidden in GitHub Actions")
    fixture = Path(fixture_path).resolve()
    if not fixture.is_file():
        raise SystemExit("Fixture file not found")
    answer = json.loads(fixture.read_text(encoding="utf-8"))
else:
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
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SystemExit(f"Model connection failed: {type(exc).__name__}") from None
try:
    proposal = extract_proposal(answer)
except ValueError as exc:
    raise SystemExit(f"Invalid model response: {exc}") from None
name=proposal.get("path","")
new=proposal.get("content","")
if name not in sources or not isinstance(new,str) or not new or new==sources[name]:
    raise SystemExit("No safe applicable change proposed")
if len(new)>60000:
    raise SystemExit("Proposed file exceeds size limit")
if name.endswith(".py"):
    try:
        ast.parse(new)
    except SyntaxError as exc:
        raise SystemExit(f"Proposed Python syntax invalid: {exc}") from None
if name.endswith(".js"):
    import subprocess
    result=subprocess.run(["node","--check","--input-type=commonjs"],input=new,text=True,capture_output=True)
    if result.returncode:
        raise SystemExit("Proposed JavaScript syntax invalid: "+result.stderr[:500])
try:
    name, new = validate_proposal(proposal, sources, cfg)
except (ValueError, SyntaxError) as exc:
    raise SystemExit(f"Unsafe proposal rejected: {exc}") from None
patch="".join(difflib.unified_diff(sources[name].splitlines(True),new.splitlines(True),fromfile="a/"+name,tofile="b/"+name))
if not patch:
    raise SystemExit("Empty patch")
out=ROOT/"agent-proposal.patch"
out.write_text(patch,encoding="utf-8")
print(f"Proposed patch for {task['id']}: {name}; {len(patch)} bytes. NO SOURCE FILES MODIFIED.")
