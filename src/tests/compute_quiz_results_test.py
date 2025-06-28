import unittest

from core.compute_quiz_results import compute_quiz_results
from core.exceptions import UserResponseError
from tests.utils.base_test_case import BaseTestCase


class ComputeQuizResultsTest(BaseTestCase):

    def test_correct_category_in_results(self):
        quiz = [
            {"question": "1 + 1", "answer": "2.0", "category": "math"},
            {"question": "2 + 2", "answer": "4.0", "category": "math"},
            {
                "question": "Day of 2023-05-04",
                "answer": "thursday",
                "category": "date",
            },
        ]
        submission = {"answer_0": "2", "answer_1": "4", "answer_2": "Thu"}
        result = compute_quiz_results(quiz, submission)
        self.assertEqual(result[0]["category"], "math")
        self.assertEqual(result[1]["category"], "math")
        self.assertEqual(result[2]["category"], "date")

    def test_all_correct_numeric(self):
        quiz = [
            {"question": "2 + 2", "answer": "4.0", "category": "math"},
            {"question": "5 * 2", "answer": "10.0", "category": "math"},
        ]
        submission = {"answer_0": "4", "answer_1": "10"}
        result = compute_quiz_results(quiz, submission)
        self.assertTrue(all(entry["is_correct"] for entry in result))

    def test_elemential_correct_numeric(self):
        quiz = [
            {"question": "2 + 3", "answer": "5.0", "category": "math"},
            {"question": "10 / 2", "answer": "5.0", "category": "math"},
        ]
        submission = {"answer_0": "5", "answer_1": "2.5"}  # incorrect
        result = compute_quiz_results(quiz, submission)
        self.assertTrue(result[0]["is_correct"])
        self.assertFalse(result[1]["is_correct"])

    def test_incorrect_format_numeric(self):
        quiz = [{"question": "3 * 3", "answer": "9.0", "category": "math"}]
        submission = {"answer_0": "nine"}
        with self.assertRaises(UserResponseError):
            compute_quiz_results(quiz, submission)

    def test_all_correct_weekdays(self):
        quiz = [
            {
                "question": "Day of 2023-05-04",
                "answer": "thursday",
                "category": "date",
            },
            {
                "question": "Day of 2023-12-25",
                "answer": "monday",
                "category": "date",
            },
        ]
        submission = {"answer_0": "Thu", "answer_1": "  MON  "}
        result = compute_quiz_results(quiz, submission)
        self.assertTrue(all(entry["is_correct"] for entry in result))

    def test_all_incorrect_weekdays(self):
        quiz = [
            {
                "question": "Day of 2023-05-04",
                "answer": "thursday",
                "category": "date",
            },
            {
                "question": "Day of 2023-12-25",
                "answer": "monday",
                "category": "date",
            },
        ]
        submission = {"answer_0": "Fri", "answer_1": "Tue"}
        result = compute_quiz_results(quiz, submission)
        self.assertFalse(any(entry["is_correct"] for entry in result))

    def test_invalid_weekday_format(self):
        quiz = [
            {
                "question": "Day of 2023-05-04",
                "answer": "thursday",
                "category": "date",
            }
        ]
        submission = {"answer_0": "Thursi"}
        with self.assertRaises(UserResponseError):
            compute_quiz_results(quiz, submission)
        submission = {"answer_0": "t"}
        with self.assertRaises(UserResponseError):
            compute_quiz_results(quiz, submission)

    def test_invalid_weekday_submission(self):
        quiz = [
            {
                "question": "Day of 2023-05-04",
                "answer": "thursday",
                "category": "date",
            }
        ]
        submission = {"answer_0": "noday"}
        with self.assertRaises(UserResponseError):
            compute_quiz_results(quiz, submission)

    def test_missing_answers_are_handled(self):
        quiz = [
            {"question": "1 + 1", "answer": "2.0", "category": "math"},
            {"question": "2 + 2", "answer": "4.0", "category": "math"},
        ]
        submission = {
            "answer_0": "2"
            # answer_1 missing
        }
        result = compute_quiz_results(quiz, submission)
        self.assertEqual(result[1]["user_answer"], "Not answered")
        self.assertFalse(result[1]["is_correct"])

    def test_float_precision_tolerance_rounding_required(self):
        quiz = [
            {
                "question": "Pi value",
                "answer": "3.1415926536",
                "category": "math",
            }
        ]
        submission = {"answer_0": "3.1416"}
        result = compute_quiz_results(quiz, submission)
        self.assertTrue(result[0]["is_correct"])

    def test_float_precision_tolerance_rounding_not_required(self):
        quiz = [
            {
                "question": "Pi value",
                "answer": "3.1415926536",
                "category": "math",
            }
        ]
        submission = {"answer_0": "3.14159"}
        result = compute_quiz_results(quiz, submission)
        self.assertTrue(result[0]["is_correct"])

    def test_float_precision_exceeded_rounding_required(self):
        quiz = [
            {
                "question": "Pi value",
                "answer": "3.1415926536",
                "category": "math",
            }
        ]
        submission = {"answer_0": "3.1415926535897"}
        result = compute_quiz_results(quiz, submission)
        self.assertTrue(result[0]["is_correct"])

    def test_float_precision_exceeded_non_rounding_required(self):
        quiz = [
            {
                "question": "Pi value",
                "answer": "3.14159265",
                "category": "math",
            }
        ]
        submission = {"answer_0": "3.1415926535897"}
        result = compute_quiz_results(quiz, submission)
        self.assertTrue(result[0]["is_correct"])

    def test_extra_answers_are_ignored(self):
        quiz = [{"question": "1 + 1", "answer": "2.0", "category": "math"}]
        submission = {"answer_0": "2", "answer_1": "999"}
        result = compute_quiz_results(quiz, submission)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["is_correct"])


if __name__ == "__main__":
    unittest.main()
