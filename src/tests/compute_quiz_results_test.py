import unittest

from src.core.compute_quiz_results import compute_quiz_results


class TestComputeQuizResults(unittest.TestCase):

    def test_all_correct_numeric(self):
        quiz = [
            {"question": "2 + 2", "answer": "4.0", "is_weekday": False},
            {"question": "5 * 2", "answer": "10.0", "is_weekday": False},
        ]
        submission = {"answer_0": "4", "answer_1": "10"}
        result = compute_quiz_results(quiz, submission)
        self.assertTrue(all(entry["is_correct"] for entry in result))

    def test_partial_correct_numeric(self):
        quiz = [
            {"question": "2 + 3", "answer": "5.0", "is_weekday": False},
            {"question": "10 / 2", "answer": "5.0", "is_weekday": False},
        ]
        submission = {"answer_0": "5", "answer_1": "2.5"}  # incorrect
        result = compute_quiz_results(quiz, submission)
        self.assertTrue(result[0]["is_correct"])
        self.assertFalse(result[1]["is_correct"])

    def test_incorrect_format_numeric(self):
        quiz = [{"question": "3 * 3", "answer": "9.0", "is_weekday": False}]
        submission = {"answer_0": "nine"}
        with self.assertRaises(ValueError):
            compute_quiz_results(quiz, submission)

    def test_all_correct_weekdays(self):
        quiz = [
            {"question": "Day of 2023-05-04", "answer": "thursday", "is_weekday": True},
            {"question": "Day of 2023-12-25", "answer": "monday", "is_weekday": True},
        ]
        submission = {"answer_0": "Thu", "answer_1": "  MON  "}
        result = compute_quiz_results(quiz, submission)
        self.assertTrue(all(entry["is_correct"] for entry in result))

    def test_invalid_weekday_submission(self):
        quiz = [
            {"question": "Day of 2023-05-04", "answer": "thursday", "is_weekday": True}
        ]
        submission = {"answer_0": "noday"}
        with self.assertRaises(ValueError):
            compute_quiz_results(quiz, submission)

    def test_missing_answers_are_handled(self):
        quiz = [
            {"question": "1 + 1", "answer": "2.0", "is_weekday": False},
            {"question": "2 + 2", "answer": "4.0", "is_weekday": False},
        ]
        submission = {
            "answer_0": "2"
            # answer_1 missing
        }
        result = compute_quiz_results(quiz, submission)
        self.assertEqual(result[1]["user_answer"], "Not answered")
        self.assertFalse(result[1]["is_correct"])

    def test_float_precision_acceptance(self):
        quiz = [{"question": "Pi value", "answer": "3.1415926535", "is_weekday": False}]
        submission = {"answer_0": "3.1415"}
        result = compute_quiz_results(quiz, submission)
        self.assertTrue(result[0]["is_correct"])

    def test_extra_answers_are_ignored(self):
        quiz = [{"question": "1 + 1", "answer": "2.0", "is_weekday": False}]
        submission = {"answer_0": "2", "answer_1": "999"}
        result = compute_quiz_results(quiz, submission)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["is_correct"])


if __name__ == "__main__":
    unittest.main()
