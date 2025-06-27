import unittest

from core.date_quiz_generator import DateQuizGenerator


class DateQuizGeneratorTest(unittest.TestCase):

    # ---------------- Test generate method ----------------
    def test_generate_date_fixed_year(self):
        blueprint = {"start_year": 2000, "end_year": 2000, "count": 3}
        quizzes = DateQuizGenerator.generate(blueprint)
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
            DateQuizGenerator.generate(blueprint)

    def test_generate_date_default_years(self):
        blueprint = {"count": 2}
        quizzes = DateQuizGenerator.generate(blueprint)
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

    # ---------------- Test compare_answer method ----------------
    def test_compare_answer_correct(self):
        test_cases = [
            ("Monday", "monday"),
            ("friday", "friday"),
            ("SUNDAY", "sunday"),
            ("tu", "Tuesday"),
            ("Wed", "wednesday"),
        ]
        for user, answer in test_cases:
            with self.subTest(user=user, answer=answer):
                self.assertTrue(DateQuizGenerator.compare_answer(user, answer))

    def test_compare_answer_incorrect(self):
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
                    DateQuizGenerator.compare_answer(user, answer)
                )

    def test_compare_answer_invalid_string(self):
        test_cases = [
            ("notaday", "monday"),
            ("12345", "tuesday"),
            ("w", "wednesday"),
        ]
        for user, answer in test_cases:
            with self.subTest(user=user, answer=answer):
                self.assertFalse(
                    DateQuizGenerator.compare_answer(user, answer)
                )

    # ---------------- Test prettify_answer method ----------------
    def test_prettify_answer(self):
        test_cases = [
            ("monday", "Monday"),
            ("tUesday", "Tuesday"),
        ]
        for user, expected in test_cases:
            with self.subTest(user=user, expected=expected):
                self.assertEqual(
                    DateQuizGenerator.prettify_answer(user), expected
                )


if __name__ == "__main__":
    unittest.main()
