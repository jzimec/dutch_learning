import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "<!-- dutch-learning-agent-state-v1 -->"


class GithubStateIntegrationTests(unittest.TestCase):
    def test_loader_restores_state_from_mocked_gh(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agent = root / "agent"
            agent.mkdir()
            (agent / "load-state.py").write_text((ROOT / "agent/load-state.py").read_text(encoding="utf-8"), encoding="utf-8")
            (agent / "tasks.json").write_text((ROOT / "agent/tasks.json").read_text(encoding="utf-8"), encoding="utf-8")
            gh = root / "gh"
            gh.write_text(
                "#!/usr/bin/env python3\n"
                "import json,sys\n"
                "args=sys.argv[1:]\n"
                "if 'list' in args: print(json.dumps([{'number':2,'title':'Dutch Learning | Agent task state'}]))\n"
                "else: print('Persistent state\\n\\n" + MARKER + "\\n' + json.dumps({'version':1,'tasks':{'AUTH-01':{'status':'in_progress'}}}))\n",
                encoding="utf-8",
            )
            gh.chmod(0o755)
            env = os.environ.copy()
            env["GITHUB_REPOSITORY"] = "test/example"
            env["PATH"] = str(root) + os.pathsep + env.get("PATH", "")
            result = subprocess.run([sys.executable, str(agent / "load-state.py")], env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            restored = json.loads((agent / "runtime-state.json").read_text(encoding="utf-8"))
            self.assertEqual(restored["tasks"]["AUTH-01"]["status"], "in_progress")

    def test_loader_rejects_done_without_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agent = root / "agent"
            agent.mkdir()
            (agent / "load-state.py").write_text((ROOT / "agent/load-state.py").read_text(encoding="utf-8"), encoding="utf-8")
            (agent / "tasks.json").write_text((ROOT / "agent/tasks.json").read_text(encoding="utf-8"), encoding="utf-8")
            gh = root / "gh"
            gh.write_text(
                "#!/usr/bin/env python3\n"
                "import json,sys\n"
                "args=sys.argv[1:]\n"
                "if 'list' in args: print(json.dumps([{'number':2,'title':'Dutch Learning | Agent task state'}]))\n"
                "else: print('State\\n\\n" + MARKER + "\\n' + json.dumps({'version':1,'tasks':{'AUTH-01':{'status':'done'}}}))\n",
                encoding="utf-8",
            )
            gh.chmod(0o755)
            env = os.environ.copy()
            env["GITHUB_REPOSITORY"] = "test/example"
            env["PATH"] = str(root) + os.pathsep + env.get("PATH", "")
            result = subprocess.run([sys.executable, str(agent / "load-state.py")], env=env, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing completion evidence", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
