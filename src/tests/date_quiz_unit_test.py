import unittest

from core.date_quiz_unit import DateQuizUnit
from core.exceptions import UserResponseError
from tests.utils.base_test_case import BaseTestCase


class DateQuizGeneratorTest(BaseTestCase):

    # ---------------- Test generate method ----------------
    def test_generate_date_fixed_year(self):
        blueprint = {"start_year": 2000, "end_year": 2000, "count": 3}
        quizzes = DateQuizUnit.generate_quiz(blueprint)
        self.assertEqual(len(quizzes), 3)
        for quiz in quizzes:
            self.assertTrue(quiz["question"].endswith("2000"))
            self.assertRegex(quiz["question"], r"\w+ \d{2}, 2000")
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

    def test_invalid_year_range_raises(self):
        blueprint = {"start_year": 2025, "end_year": 2020, "count": 1}
        with self.assertRaises(AssertionError):
            DateQuizUnit.generate_quiz(blueprint)

    def test_generate_date_default_years(self):
        blueprint = {"count": 2}
        quizzes = DateQuizUnit.generate_quiz(blueprint)
        self.assertEqual(len(quizzes), 2)
        for quiz in quizzes:
            self.assertRegex(quiz["question"], r"\w+ \d{2}, \d{4}")
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

    # ---------------- Test compare_answers method ----------------
    def test_compare_answers_correct(self):
        test_cases = [
            ("Monday", "monday"),
            ("friday", "friday"),
            ("SUNDAY", "sunday"),
            ("tu", "Tuesday"),
            ("Wed", "wednesday"),
        ]
        for user, answer in test_cases:
            with self.subTest(user=user, answer=answer):
                self.assertTrue(DateQuizUnit.compare_answers(user, answer))

    def test_compare_answers_incorrect(self):
        test_cases = [
            ("Monday", "tuesday"),
            ("friday", "saturday"),
            ("sunday", "monday"),
            ("tu", "wednesday"),
            ("Wed", "thursday"),
        ]
        for user, answer in test_cases:
            with self.subTest(user=user, answer=answer):
                self.assertFalse(
                    DateQuizUnit.compare_answers(user, answer)
                )

    def test_compare_answers_invalid_string(self):
        test_cases = [
            ("notaday", "monday"),
            ("12345", "tuesday"),
            ("w", "wednesday"),
        ]
        for user, answer in test_cases:
            with self.subTest(user=user, answer=answer):
                self.assertFalse(
                    DateQuizUnit.compare_answers(user, answer)
                )

    # ---------------- Test parse_user_answer method ----------------
    def test_parse_user_answer_valid(self):
        test_cases = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for user in test_cases:
            with self.subTest(user=user):
                self.assertEqual(
                    DateQuizUnit.parse_user_answer(user), user.lower()
                )

    def test_parse_user_answer_invalid(self):
        test_cases = [
            "notaday",
            "12345",
            "w",
            "tuesday!",
        ]
        for user in test_cases:
            with self.subTest(user=user):
                with self.assertRaises(UserResponseError):
                    DateQuizUnit.parse_user_answer(user)

    # ---------------- Test prettify_answer method ----------------
    def test_prettify_answer(self):
        test_cases = [
            ("monday", "Monday"),
            ("tUesday", "Tuesday"),
        ]
        for user, expected in test_cases:
            with self.subTest(user=user, expected=expected):
                self.assertEqual(
                    DateQuizUnit.prettify_answer(user), expected
                )


if __name__ == "__main__":
    unittest.main()
