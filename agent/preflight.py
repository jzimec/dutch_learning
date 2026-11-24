#!/usr/bin/env python3
"""Preflight checks for supervised AI proposals. Never print secrets."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
config = json.loads((ROOT / "agent/runner-config.json").read_text(encoding="utf-8"))
tasks = json.loads((ROOT / "agent/tasks.json").read_text(encoding="utf-8"))["tasks"]
eligible = sorted((t for t in tasks if t["status"] in ("todo", "in_progress")), key=lambda t: (t["priority"], t["id"]))
problems = []
if config.get("mode") != "supervised" or config.get("auto_push") is not False or config.get("auto_merge") is not False:
    problems.append("Unsafe runner mode or automatic write permissions")
if not eligible:
    problems.append("No runnable task")
elif eligible[0]["id"] != "AUTH-01":
    problems.append("Current AI proposer supports AUTH-01 only")
source = ROOT / "dutch-auth.js"
if not source.is_file() or source.stat().st_size > 40000:
    problems.append("Required auth source missing or too large")
if not os.environ.get("OPENAI_API_KEY", "").strip():
    problems.append("OPENAI_API_KEY GitHub Actions secret is not configured")
if problems:
    for problem in problems:
        print("PREFLIGHT BLOCKED: " + problem)
    sys.exit(1)
print("PREFLIGHT PASS: required secret present; scope and safety configuration checked.")
print("No model call made and no source files modified.")
