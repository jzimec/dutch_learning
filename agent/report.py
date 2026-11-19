#!/usr/bin/env python3
"""Write a deterministic agent progress report. Does not claim AI work was run."""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent.parent
queue = json.loads((root / "agent/tasks.json").read_text(encoding="utf-8"))
counts = Counter(t["status"] for t in queue["tasks"])
lines = [
    "# Dutch Learning agent supervisor",
    "",
    f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
    "",
    "## Current tasks",
    "",
]
for task in sorted(queue["tasks"], key=lambda t: (t["priority"], t["id"])):
    lines.append(f"- {task['id']} | {task['status']} | {task['title']}")
    if task.get("blocked_by"):
        lines.append(f"  - Blocker: {task['blocked_by']}")
lines.extend([
    "",
    "## Summary",
    "",
    *[f"- {status}: {count}" for status, count in sorted(counts.items())],
    "",
    "## Execution capability",
    "",
    "- Automated syntax and safety tests: configured",
    "- Task selection: configured",
    "- AI code proposals: manual workflow only; no automatic model invocation",
    "- Autonomous source modification and production deployment: disabled",
    "- Scheduled GitHub Actions only execute from the repository default branch",
    "",
])
report = "\n".join(lines)
(root / "agent-supervisor-report.md").write_text(report, encoding="utf-8")
print(report)
