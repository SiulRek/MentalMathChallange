import unittest

from core import generate_quiz, compute_quiz_results
from core.exceptions import UserResponseError
from tests.utils.base_test_case import BaseTestCase


class GenerateQuizTest(BaseTestCase):
    def test_generate_quiz_math(self):
        blueprint = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "int", "start": 1, "end": 1},
                        {"type": "operator", "value": "+"},
                        {"type": "int", "start": 1, "end": 1},
                    ],
                },
                2,
            )
        ]
        result = generate_quiz(blueprint)
        self.assertEqual(len(result), 2)
        for quiz in result:
            self.assertEqual(quiz["question"], "1 + 1")
            self.assertEqual(quiz["answer"], "2")
            self.assertEqual(quiz["category"], "math")

    def test_generate_quiz_date(self):
        blueprint = [
            (
                {"category": "date", "start_year": 2000, "end_year": 2000},
                1,
            )
        ]
        result = generate_quiz(blueprint)
        self.assertEqual(len(result), 1)
        quiz = result[0]
        self.assertTrue(quiz["question"].endswith("2000"))
        self.assertIn(
            quiz["answer"],
            [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
        )
        self.assertEqual(quiz["category"], "date")

    def test_generate_quiz_mixed_math_and_date(self):
        blueprint = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "int", "start": 1, "end": 1},
                        {"type": "operator", "value": "+"},
                        {"type": "int", "start": 1, "end": 1},
                    ],
                },
                1,
            ),
            (
                {
                    "category": "date",
                    "start_year": 2000,
                    "end_year": 2000,
                },
                1,
            ),
        ]
        result = generate_quiz(blueprint)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["category"], "math")
        self.assertEqual(result[0]["question"], "1 + 1")
        self.assertEqual(result[0]["answer"], "2")
        self.assertEqual(result[1]["category"], "date")
        self.assertTrue(result[1]["question"].endswith("2000"))


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
        user_answers = ["2", "4", "Thu"]
        result = compute_quiz_results(quiz, user_answers)
        self.assertEqual(result[0]["category"], "math")
        self.assertEqual(result[1]["category"], "math")
        self.assertEqual(result[2]["category"], "date")

    def test_all_correct_numeric(self):
        quiz = [
            {"question": "2 + 2", "answer": "4.0", "category": "math"},
            {"question": "5 * 2", "answer": "10.0", "category": "math"},
        ]
        user_answers = ["4", "10"]
        result = compute_quiz_results(quiz, user_answers)
        self.assertTrue(all(entry["is_correct"] for entry in result))

    def test_elemential_correct_numeric(self):
        quiz = [
            {"question": "2 + 3", "answer": "5.0", "category": "math"},
            {"question": "10 / 2", "answer": "5.0", "category": "math"},
        ]
        user_answers = ["5", "2.5"]  # Second answer incorrect
        result = compute_quiz_results(quiz, user_answers)
        self.assertTrue(result[0]["is_correct"])
        self.assertFalse(result[1]["is_correct"])

    def test_incorrect_format_numeric(self):
        quiz = [{"question": "3 * 3", "answer": "9.0", "category": "math"}]
        user_answers = ["nine"]
        with self.assertRaises(UserResponseError):
            compute_quiz_results(quiz, user_answers)

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
        user_answers = ["Thu", "  MON  "]
        result = compute_quiz_results(quiz, user_answers)
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
        user_answers = ["Fri", "Tue"]
        result = compute_quiz_results(quiz, user_answers)
        self.assertFalse(any(entry["is_correct"] for entry in result))

    def test_invalid_weekday_format(self):
        quiz = [
            {
                "question": "Day of 2023-05-04",
                "answer": "thursday",
                "category": "date",
            }
        ]
        with self.assertRaises(UserResponseError):
            compute_quiz_results(quiz, ["Thursi"])
        with self.assertRaises(UserResponseError):
            compute_quiz_results(quiz, ["t"])

    def test_invalid_weekday_submission(self):
        quiz = [
            {
                "question": "Day of 2023-05-04",
                "answer": "thursday",
                "category": "date",
            }
        ]
        with self.assertRaises(UserResponseError):
            compute_quiz_results(quiz, ["noday"])

    def test_missing_answers_are_handled(self):
        quiz = [
            {"question": "1 + 1", "answer": "2.0", "category": "math"},
            {"question": "2 + 2", "answer": "4.0", "category": "math"},
        ]
        user_answers = ["2", ""]  # Simulate missing
        with self.assertRaises(UserResponseError):
            compute_quiz_results(quiz, user_answers)

    def test_float_precision_tolerance_rounding_required(self):
        quiz = [
            {
                "question": "Pi value",
                "answer": "3.1415926536",
                "category": "math",
            }
        ]
        user_answers = ["3.1416"]
        result = compute_quiz_results(quiz, user_answers)
        self.assertTrue(result[0]["is_correct"])

    def test_float_precision_tolerance_rounding_not_required(self):
        quiz = [
            {
                "question": "Pi value",
                "answer": "3.1415926536",
                "category": "math",
            }
        ]
        user_answers = ["3.14159"]
        result = compute_quiz_results(quiz, user_answers)
        self.assertTrue(result[0]["is_correct"])

    def test_float_precision_exceeded_rounding_required(self):
        quiz = [
            {
                "question": "Pi value",
                "answer": "3.1415926536",
                "category": "math",
            }
        ]
        user_answers = ["3.1415926535897"]
        result = compute_quiz_results(quiz, user_answers)
        self.assertTrue(result[0]["is_correct"])

    def test_float_precision_exceeded_non_rounding_required(self):
        quiz = [
            {
                "question": "Pi value",
                "answer": "3.14159265",
                "category": "math",
            }
        ]
        user_answers = ["3.1415926535897"]
        result = compute_quiz_results(quiz, user_answers)
        self.assertTrue(result[0]["is_correct"])

    def test_extra_answers_are_ignored(self):
        quiz = [{"question": "1 + 1", "answer": "2.0", "category": "math"}]
        user_answers = ["2", "999"]
        result = compute_quiz_results(quiz, user_answers)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["is_correct"])


if __name__ == "__main__":
    unittest.main()
