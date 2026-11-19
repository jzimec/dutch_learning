"""Append-only local agent execution journal with atomic writes."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

MAX_RECORDS = 500


def append_record(path, record):
    path = Path(path)
    if not isinstance(record, dict) or not record.get("task_id") or not record.get("result"):
        raise ValueError("Record needs task_id and result")
    if path.exists():
        history = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(history, list):
            raise ValueError("Invalid journal format")
    else:
        history = []
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_id": str(record["task_id"]),
        "result": str(record["result"]),
        "commit": str(record.get("commit", "")),
        "test_run": str(record.get("test_run", "")),
        "blocker": str(record.get("blocker", "")),
    }
    history = (history + [entry])[-MAX_RECORDS:]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return entry
