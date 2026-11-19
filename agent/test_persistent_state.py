import json
import tempfile
import unittest
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


class PersistentSelectionTests(unittest.TestCase):
    def test_completed_task_is_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            (base/"tasks.json").write_text((ROOT/"agent/tasks.json").read_text(encoding="utf-8"),encoding="utf-8")
            (base/"next_task.py").write_text((ROOT/"agent/next_task.py").read_text(encoding="utf-8"),encoding="utf-8")
            state={"version":1,"tasks":{"AUTH-01":{"status":"done","evidence":"CI run 123 passed"}}}
            (base/"runtime-state.json").write_text(json.dumps(state),encoding="utf-8")
            result=subprocess.run([sys.executable,str(base/"next_task.py")],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn("UI-01",result.stdout)
            self.assertNotIn("Next task: AUTH-01",result.stdout)

    def test_completion_without_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            (base/"tasks.json").write_text((ROOT/"agent/tasks.json").read_text(encoding="utf-8"),encoding="utf-8")
            (base/"next_task.py").write_text((ROOT/"agent/next_task.py").read_text(encoding="utf-8"),encoding="utf-8")
            (base/"runtime-state.json").write_text(json.dumps({"version":1,"tasks":{"AUTH-01":{"status":"done"}}}),encoding="utf-8")
            result=subprocess.run([sys.executable,str(base/"next_task.py")],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(result.returncode,0)
            self.assertIn("lacks evidence",result.stderr+result.stdout)


if __name__=="__main__":
    unittest.main()
