import unittest

from core.date_quiz_generator import DateQuizGenerator


class DateQuizGeneratorTest(unittest.TestCase):
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

    def test_compare_answer_correct(self):
        self.assertTrue(DateQuizGenerator.compare_answer("Monday", "monday"))
        self.assertTrue(DateQuizGenerator.compare_answer("friday", "friday"))
        self.assertTrue(DateQuizGenerator.compare_answer("SUNDAY", "sunday"))

    def test_compare_answer_invalid_string(self):
        self.assertFalse(DateQuizGenerator.compare_answer("notaday", "monday"))

    def test_invalid_year_range_raises(self):
        blueprint = {"start_year": 2025, "end_year": 2020, "count": 1}
        with self.assertRaises(AssertionError):
            DateQuizGenerator.generate(blueprint)


if __name__ == "__main__":
    unittest.main()
