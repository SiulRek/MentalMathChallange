import unittest

from core.quiz_utils import generate_quiz, compare_answers


class QuizUtilsTest(unittest.TestCase):
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
            ["monday", "tuesday", "wednesday", "thursday",
             "friday", "saturday", "sunday"]
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

    def test_compare_math_true(self):
        self.assertTrue(compare_answers("2", "2.0", "math"))
        self.assertFalse(compare_answers("5", "2", "math"))

    def test_compare_date_true(self):
        self.assertTrue(compare_answers("Monday", "monday", "date"))
        self.assertFalse(compare_answers("notaday", "monday", "date"))

    def test_invalid_category_raises(self):
        with self.assertRaises(ValueError):
            generate_quiz([({"category": "invalid"}, 1)])

        with self.assertRaises(ValueError):
            compare_answers("x", "y", "invalid")


if __name__ == "__main__":
    unittest.main()
