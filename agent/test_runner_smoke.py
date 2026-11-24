import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class RunnerSmokeTests(unittest.TestCase):
    def test_no_api_key_fails_closed(self):
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None)
        result = subprocess.run(
            [sys.executable, str(ROOT / "agent/propose.py")],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=15,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("OPENAI_API_KEY missing", result.stdout + result.stderr)
        self.assertFalse((ROOT / "agent-proposal.patch").exists())


if __name__ == "__main__":
    unittest.main()
