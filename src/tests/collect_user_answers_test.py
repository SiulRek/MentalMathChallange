import unittest

from app.collect_user_answers import collect_user_answers
from tests.utils.base_test_case import BaseTestCase


class CollectUserAnswersTest(BaseTestCase):
    def test_all_answers_present_in_order(self):
        submission = {"answer_0": "A", "answer_1": "B", "answer_2": "C"}
        expected = ["A", "B", "C"]
        result = collect_user_answers(submission, 3)
        self.assertEqual(result, expected)

    def test_answers_missing_keys(self):
        submission = {"answer_0": "A", "answer_2": "C"}
        expected = ["A", "", "C"]
        result = collect_user_answers(submission, 3)
        self.assertEqual(result, expected)

    def test_extra_unexpected_keys_ignored(self):
        submission = {
            "answer_0": "A",
            "answer_1": "B",
            "answer_2": "C",
            "unexpected": "D",
        }
        expected = ["A", "B", "C"]
        result = collect_user_answers(submission, 3)
        self.assertEqual(result, expected)

    def test_invalid_key_format_raises(self):
        submission = {
            "answer_0": "A",
            "ans_1": "B",  # Invalid format, not starting with answer_
        }
        # Should ignore invalid keys silently because they don't start with
        # "answer_"
        expected = ["A", ""]
        result = collect_user_answers(submission, 2)
        self.assertEqual(result, expected)

        # But if prefix matches and suffix is malformed, should raise
        submission = {"answer_one": "A"}
        with self.assertRaises(ValueError):
            collect_user_answers(submission, 1)

    def test_empty_submission_populates_empty_answers(self):
        submission = {}
        expected = ["", "", ""]
        result = collect_user_answers(submission, 3)
        self.assertEqual(result, expected)

    def test_non_integer_index_raises(self):
        submission = {"answer_one": "A"}
        with self.assertRaises(ValueError):
            collect_user_answers(submission, 1)

    def test_answers_out_of_order_sorted_correctly(self):
        submission = {"answer_2": "C", "answer_0": "A", "answer_1": "B"}
        expected = ["A", "B", "C"]
        result = collect_user_answers(submission, 3)
        self.assertEqual(result, expected)

    def test_index_out_of_range_ignored(self):
        submission = {
            "answer_0": "A",
            "answer_1": "B",
            "answer_3": "D",  # Out of range
        }
        expected = ["A", "B"]
        with self.assertWarns(UserWarning):
            result = collect_user_answers(submission, 2)
        result = collect_user_answers(submission, 2)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
