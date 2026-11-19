import unittest
from response_parser import extract_proposal


class ModelResponseTests(unittest.TestCase):
    def test_completed_response(self):
        answer={"status":"completed","output":[{"type":"message","content":[{"type":"output_text","text":'{"path":"dutch-auth.js","content":"const a=1;"}'}]}]}
        self.assertEqual(extract_proposal(answer)["path"],"dutch-auth.js")

    def test_reject_incomplete_response(self):
        with self.assertRaises(ValueError):
            extract_proposal({"status":"incomplete","output":[]})

    def test_reject_empty_response(self):
        with self.assertRaises(ValueError):
            extract_proposal({"status":"completed","output":[]})

    def test_reject_invalid_json(self):
        with self.assertRaises(ValueError):
            extract_proposal({"status":"completed","output":[{"type":"message","content":[{"type":"output_text","text":"not json"}]}]})

    def test_reject_unexpected_fields(self):
        with self.assertRaises(ValueError):
            extract_proposal({"status":"completed","output":[{"type":"message","content":[{"type":"output_text","text":'{"path":"x","content":"y","extra":1}'}]}]})


if __name__=="__main__":
    unittest.main()
