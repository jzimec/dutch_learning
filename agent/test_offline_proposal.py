import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class OfflineProposalTests(unittest.TestCase):
    def test_full_proposal_pipeline_without_network_or_source_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp)
            shutil.copytree(ROOT / "agent", sandbox / "agent")
            original = (ROOT / "dutch-auth.js").read_text(encoding="utf-8")
            (sandbox / "dutch-auth.js").write_text(original, encoding="utf-8")
            changed = original + "\n// Offline test-only comment.\n"
            response = {
                "status": "completed",
                "output": [{"type": "message", "content": [
                    {"type": "output_text", "text": json.dumps({"path": "dutch-auth.js", "content": changed})}
                ]}],
            }
            fixture = sandbox / "response.json"
            fixture.write_text(json.dumps(response), encoding="utf-8")
            env = os.environ.copy()
            env.pop("OPENAI_API_KEY", None)
            env.pop("GITHUB_ACTIONS", None)
            env["AGENT_RESPONSE_FIXTURE"] = str(fixture)
            result = subprocess.run(
                [sys.executable, str(sandbox / "agent/propose.py")],
                cwd=sandbox, env=env, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            patch = (sandbox / "agent-proposal.patch").read_text(encoding="utf-8")
            self.assertIn("Offline test-only comment", patch)
            self.assertEqual((sandbox / "dutch-auth.js").read_text(encoding="utf-8"), original)

    def test_fixture_forbidden_in_github_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp)
            shutil.copytree(ROOT / "agent", sandbox / "agent")
            (sandbox / "dutch-auth.js").write_text((ROOT / "dutch-auth.js").read_text(encoding="utf-8"), encoding="utf-8")
            fixture = sandbox / "response.json"
            fixture.write_text("{}", encoding="utf-8")
            env = os.environ.copy()
            env["AGENT_RESPONSE_FIXTURE"] = str(fixture)
            env["GITHUB_ACTIONS"] = "true"
            result = subprocess.run(
                [sys.executable, str(sandbox / "agent/propose.py")],
                cwd=sandbox, env=env, capture_output=True, text=True, timeout=30,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Fixture mode forbidden", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
