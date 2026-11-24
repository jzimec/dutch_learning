import unittest
from state import transition


class StateTests(unittest.TestCase):
    def setUp(self):
        self.task = {"id": "AUTH-01", "status": "todo", "title": "Test auth"}

    def test_start_task(self):
        updated = transition(self.task, "in_progress")
        self.assertEqual(updated["status"], "in_progress")
        self.assertEqual(self.task["status"], "todo")

    def test_cannot_complete_without_evidence(self):
        active = transition(self.task, "in_progress")
        with self.assertRaises(ValueError):
            transition(active, "done")

    def test_complete_with_evidence(self):
        active = transition(self.task, "in_progress")
        done = transition(active, "done", evidence="GitHub Actions run #123 passed")
        self.assertEqual(done["status"], "done")

    def test_cannot_reopen_done_task(self):
        active = transition(self.task, "in_progress")
        done = transition(active, "done", evidence="test passed")
        with self.assertRaises(ValueError):
            transition(done, "todo")

    def test_blocked_can_return_to_queue(self):
        blocked = transition(self.task, "blocked")
        self.assertEqual(transition(blocked, "todo")["status"], "todo")


if __name__ == "__main__":
    unittest.main()
