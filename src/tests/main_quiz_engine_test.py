import unittest

from core.exceptions import UserResponseError
from core.main_quiz_engine import MainQuizEngine
from tests.utils.base_test_case import BaseTestCase

# NOTE: The logic for generating quizzes and computing results is not tested
# here, as it is covered in the public_core_test.py file.


class CompareAnswersTest(BaseTestCase):
    def setUp(self):
        self.quiz_engine = MainQuizEngine()

    def test_compare_math_true(self):
        self.quiz_engine._focus_on_category("math")
        self.assertTrue(self.quiz_engine._compare_answers("2", "2.0"))
        self.assertFalse(self.quiz_engine._compare_answers("5", "2"))

    def test_compare_date_true(self):
        self.quiz_engine._focus_on_category("date")
        self.assertTrue(self.quiz_engine._compare_answers("Monday", "monday"))
        self.assertFalse(
            self.quiz_engine._compare_answers("notaday", "monday")
        )

    def test_compare_empty(self):
        self.quiz_engine._focus_on_category("math")
        self.assertFalse(self.quiz_engine._compare_answers("", "2"))
        self.assertFalse(self.quiz_engine._compare_answers("2", ""))
        self.assertFalse(self.quiz_engine._compare_answers(None, ""))

    def test_compare_without_focus_raises(self):
        with self.assertRaises(ValueError):
            self.quiz_engine._compare_answers("2", "2")


class ParseUserAnswerTest(BaseTestCase):
    def setUp(self):
        self.quiz_engine = MainQuizEngine()

    def test_parse_user_answer_math(self):
        self.quiz_engine._focus_on_category("math")
        self.assertEqual(
            self.quiz_engine._parse_user_answer("2.0000"), "2.0000"
        )
        self.assertEqual(
            self.quiz_engine._parse_user_answer("3.1400"), "3.1400"
        )
        with self.assertRaises(UserResponseError):
            self.quiz_engine._parse_user_answer("notanumber")

    def test_parse_user_answer_date(self):
        self.quiz_engine._focus_on_category("date")
        self.assertEqual(
            self.quiz_engine._parse_user_answer("Monday"), "monday"
        )
        self.assertEqual(self.quiz_engine._parse_user_answer("tu"), "tuesday")
        with self.assertRaises(UserResponseError):
            self.quiz_engine._parse_user_answer("notaday")

    def test_parse_without_focus_raises(self):
        with self.assertRaises(ValueError):
            self.quiz_engine._parse_user_answer("Monday")


class PrettifyAnswerTest(BaseTestCase):
    def setUp(self):
        self.quiz_engine = MainQuizEngine()

    def test_prettify_answer_math(self):
        self.quiz_engine._focus_on_category("math")
        self.assertEqual(self.quiz_engine._prettify_answer("2.0000"), "2")
        self.assertEqual(self.quiz_engine._prettify_answer("3.1400"), "3.14")
        self.assertIsNone(self.quiz_engine._prettify_answer(""))
        self.assertIsNone(self.quiz_engine._prettify_answer(None))

    def test_prettify_answer_date(self):
        self.quiz_engine._focus_on_category("date")
        self.assertEqual(self.quiz_engine._prettify_answer("Monday"), "Monday")
        self.assertEqual(
            self.quiz_engine._prettify_answer("tuesday"), "Tuesday"
        )
        self.assertIsNone(self.quiz_engine._prettify_answer(""))
        self.assertIsNone(self.quiz_engine._prettify_answer(None))

    def test_prettify_without_focus_raises(self):
        with self.assertRaises(ValueError):
            self.quiz_engine._prettify_answer("Monday")


if __name__ == "__main__":
    unittest.main()
