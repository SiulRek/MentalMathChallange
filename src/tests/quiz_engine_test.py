import unittest

from core.exceptions import UserResponseError
from core.quiz_engine import QuizEngine
from tests.utils.base_test_case import BaseTestCase


class GenerateQuizTest(BaseTestCase):
    def setUp(self):
        self.quiz_engine = QuizEngine()

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
        result = self.quiz_engine.generate(blueprint)
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
        result = self.quiz_engine.generate(blueprint)
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
        result = self.quiz_engine.generate(blueprint)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["category"], "math")
        self.assertEqual(result[0]["question"], "1 + 1")
        self.assertEqual(result[0]["answer"], "2")
        self.assertEqual(result[1]["category"], "date")
        self.assertTrue(result[1]["question"].endswith("2000"))


class CompareAnswersTest(BaseTestCase):
    def setUp(self):
        self.quiz_engine = QuizEngine()

    def test_compare_math_true(self):
        self.quiz_engine.focus_on_category("math")
        self.assertTrue(self.quiz_engine.compare_answers("2", "2.0"))
        self.assertFalse(self.quiz_engine.compare_answers("5", "2"))

    def test_compare_date_true(self):
        self.quiz_engine.focus_on_category("date")
        self.assertTrue(
            self.quiz_engine.compare_answers("Monday", "monday")
        )
        self.assertFalse(
            self.quiz_engine.compare_answers("notaday", "monday")
        )

    def test_compare_empty(self):
        self.quiz_engine.focus_on_category("math")
        self.assertFalse(self.quiz_engine.compare_answers("", "2"))
        self.assertFalse(self.quiz_engine.compare_answers("2", ""))
        self.assertFalse(self.quiz_engine.compare_answers(None, ""))

    def test_compare_without_focus_raises(self):
        with self.assertRaises(ValueError):
            self.quiz_engine.compare_answers("2", "2")


class ParseUserAnswerTest(BaseTestCase):
    def setUp(self):
        self.quiz_engine = QuizEngine()

    def test_parse_user_answer_math(self):
        self.quiz_engine.focus_on_category("math")
        self.assertEqual(
            self.quiz_engine.parse_user_answer("2.0000"), "2.0000"
        )
        self.assertEqual(
            self.quiz_engine.parse_user_answer("3.1400"), "3.1400"
        )
        with self.assertRaises(UserResponseError):
            self.quiz_engine.parse_user_answer("notanumber")

    def test_parse_user_answer_date(self):
        self.quiz_engine.focus_on_category("date")
        self.assertEqual(
            self.quiz_engine.parse_user_answer("Monday"), "monday"
        )
        self.assertEqual(
            self.quiz_engine.parse_user_answer("tu"), "tuesday"
        )
        with self.assertRaises(UserResponseError):
            self.quiz_engine.parse_user_answer("notaday")

    def test_parse_without_focus_raises(self):
        with self.assertRaises(ValueError):
            self.quiz_engine.parse_user_answer("Monday")


class PrettifyAnswerTest(BaseTestCase):
    def setUp(self):
        self.quiz_engine = QuizEngine()

    def test_prettify_answer_math(self):
        self.quiz_engine.focus_on_category("math")
        self.assertEqual(self.quiz_engine.prettify_answer("2.0000"), "2")
        self.assertEqual(self.quiz_engine.prettify_answer("3.1400"), "3.14")
        self.assertIsNone(self.quiz_engine.prettify_answer(""))
        self.assertIsNone(self.quiz_engine.prettify_answer(None))

    def test_prettify_answer_date(self):
        self.quiz_engine.focus_on_category("date")
        self.assertEqual(
            self.quiz_engine.prettify_answer("Monday"), "Monday"
        )
        self.assertEqual(
            self.quiz_engine.prettify_answer("tuesday"), "Tuesday"
        )
        self.assertIsNone(self.quiz_engine.prettify_answer(""))
        self.assertIsNone(self.quiz_engine.prettify_answer(None))

    def test_prettify_without_focus_raises(self):
        with self.assertRaises(ValueError):
            self.quiz_engine.prettify_answer("Monday")


if __name__ == "__main__":
    unittest.main()
