import unittest

from core.exceptions import UserResponseError
from core.quiz_utils import (
    generate_quiz,
    compare_answers,
    parse_user_answer,
    prettify_answer,
)
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


class CompareAnswersTest(BaseTestCase):
    def test_compare_math_true(self):
        self.assertTrue(compare_answers("2", "2.0", "math"))
        self.assertFalse(compare_answers("5", "2", "math"))

    def test_compare_date_true(self):
        self.assertTrue(compare_answers("Monday", "monday", "date"))
        self.assertFalse(compare_answers("notaday", "monday", "date"))

    def test_compare_empty(self):
        self.assertFalse(compare_answers("", "2", "math"))
        self.assertFalse(compare_answers("2", "", "date"))
        self.assertFalse(compare_answers(None, "", "math"))


class ParseUserAnswerTest(BaseTestCase):
    def test_parse_user_answer_math(self):
        self.assertEqual(parse_user_answer("2.0000", "math"), "2.0000")
        self.assertEqual(parse_user_answer("3.1400", "math"), "3.1400")
        with self.assertRaises(UserResponseError):
            parse_user_answer("notanumber", "math")

    def test_parse_user_answer_date(self):
        self.assertEqual(parse_user_answer("Monday", "date"), "monday")
        self.assertEqual(parse_user_answer("tu", "date"), "tuesday")
        with self.assertRaises(UserResponseError):
            parse_user_answer("notaday", "date")


class PrettifyAnswerTest(BaseTestCase):
    def test_prettify_answer_math(self):
        self.assertEqual(prettify_answer("2.0000", "math"), "2")
        self.assertEqual(prettify_answer("3.1400", "math"), "3.14")
        self.assertIsNone(prettify_answer("", "math"))
        self.assertIsNone(prettify_answer(None, "math"))

    def test_prettify_answer_date(self):
        self.assertEqual(prettify_answer("Monday", "date"), "Monday")
        self.assertEqual(prettify_answer("tuesday", "date"), "Tuesday")
        self.assertIsNone(prettify_answer("", "date"))
        self.assertIsNone(prettify_answer(None, "date"))


if __name__ == "__main__":
    unittest.main()
