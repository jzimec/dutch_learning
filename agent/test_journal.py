import json
import tempfile
import unittest
from pathlib import Path
from journal import append_record


class JournalTests(unittest.TestCase):
    def test_append_preserves_previous_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            append_record(path, {"task_id": "AUTH-01", "result": "started"})
            append_record(path, {"task_id": "AUTH-01", "result": "blocked", "blocker": "no test credentials"})
            records = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(records), 2)
            self.assertEqual(records[1]["blocker"], "no test credentials")

    def test_reject_missing_task_id(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                append_record(Path(directory) / "history.json", {"result": "done"})

    def test_reject_invalid_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            path.write_text("{}")
            with self.assertRaises(ValueError):
                append_record(path, {"task_id": "X", "result": "blocked"})


if __name__ == "__main__":
    unittest.main()
