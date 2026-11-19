import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PreflightTests(unittest.TestCase):
    def run_preflight(self, key=None):
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None)
        if key is not None:
            env["OPENAI_API_KEY"] = key
        return subprocess.run(
            [sys.executable, str(ROOT / "agent/preflight.py")],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=10,
        )

    def test_missing_secret_blocks_without_leaking(self):
        result = self.run_preflight()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not configured", result.stdout)

    def test_secret_present_passes_without_leaking(self):
        secret = "test-secret-never-print-this"
        result = self.run_preflight(secret)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn(secret, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
