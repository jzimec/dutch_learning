import unittest
from validate_proposal import validate_proposal

CONFIG = {
    "allowed_paths": ["dutch-auth.js", "agent/**"],
    "protected_paths": ["index.html", ".github/workflows/**"],
}
SOURCES = {"dutch-auth.js": "const ok = true;\n", "index.html": "<html></html>"}


class ProposalValidationTests(unittest.TestCase):
    def test_valid_javascript(self):
        name, code = validate_proposal(
            {"path": "dutch-auth.js", "content": "const ok = false;\n"},
            SOURCES, CONFIG,
        )
        self.assertEqual(name, "dutch-auth.js")
        self.assertIn("false", code)

    def test_reject_protected_file(self):
        with self.assertRaises(ValueError):
            validate_proposal(
                {"path": "index.html", "content": "<html>changed</html>"},
                SOURCES, CONFIG,
            )

    def test_reject_unknown_file(self):
        with self.assertRaises(ValueError):
            validate_proposal(
                {"path": "other.js", "content": "const x = 1;"},
                SOURCES, CONFIG,
            )

    def test_reject_invalid_javascript(self):
        with self.assertRaises(ValueError):
            validate_proposal(
                {"path": "dutch-auth.js", "content": "const = ;"},
                SOURCES, CONFIG,
            )

    def test_reject_unchanged_file(self):
        with self.assertRaises(ValueError):
            validate_proposal(
                {"path": "dutch-auth.js", "content": SOURCES["dutch-auth.js"]},
                SOURCES, CONFIG,
            )


if __name__ == "__main__":
    unittest.main()
