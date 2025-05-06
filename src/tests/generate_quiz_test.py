import unittest

from src.core.generate_quiz import generate_quiz, UserConfigError
from src.tests.utils.base_test_case import BaseTestCase


class TestGenerateQuiz(BaseTestCase):

    def test_generate_single_math_quiz_hardcoded(self):
        config = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "int", "start": 2, "end": 2},
                        {"type": "operator", "value": "+"},
                        {"type": "int", "start": 3, "end": 3},
                    ],
                },
                1,
            )
        ]
        quiz = generate_quiz(config)
        self.assertEqual(len(quiz), 1)
        self.assertEqual(quiz[0]["question"], "2 + 3")
        self.assertEqual(quiz[0]["answer"], "5")
        self.assertFalse(quiz[0]["is_weekday"])

    def test_generate_multiple_quizzes_fixed_output(self):
        config = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "int", "start": 1, "end": 1},
                        {"type": "operator", "value": "*"},
                        {"type": "int", "start": 5, "end": 5},
                    ],
                },
                3,
            )
        ]
        quiz = generate_quiz(config)
        self.assertEqual(len(quiz), 3)
        for q in quiz:
            self.assertEqual(q["question"], "1 * 5")
            self.assertEqual(q["answer"], "5")
            self.assertFalse(q["is_weekday"])

    def test_generate_date_question(self):
        config = [
            (
                {"category": "date", "start_year": 2000, "end_year": 2000},
                3,
            )
        ]
        quiz = generate_quiz(config)
        self.assertEqual(len(quiz), 3)
        for q in quiz:
            self.assertTrue(q["is_weekday"])
            self.assertRegex(q["question"], r"\d{4}-\d{2}-\d{2}")
            self.assertIn(
                q["answer"],
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

    def test_invalid_expr_type_raises(self):
        config = [({"category": "invalid_type"}, 1)]
        with self.assertRaises(ValueError):
            generate_quiz(config)

    def test_invalid_operator_raises(self):
        config = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "int", "start": 1, "end": 5},
                        {"type": "operator", "value": "^^"},
                        {"type": "int", "start": 1, "end": 5},
                    ],
                },
                1,
            )
        ]
        with self.assertRaises(UserConfigError):
            generate_quiz(config)

    def test_step_rescaling_logic(self):
        config = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "float", "start": 1.0, "end": 1.0},
                        {"type": "operator", "value": "+"},
                        {"type": "float", "start": 2.0, "end": 2.0},
                    ],
                },
                1,
            )
        ]
        quiz = generate_quiz(config)
        self.assertEqual(len(quiz), 1)
        question = quiz[0]["question"]
        self.assertTrue(
            question.startswith("1.0 + 2.0") or question.startswith("1 + 2")
        )
        self.assertEqual(quiz[0]["answer"], "3")

    def test_zero_division_handling(self):
        config = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "int", "start": 1, "end": 1},
                        {"type": "operator", "value": "/"},
                        {"type": "int", "start": 0, "end": 0},
                    ],
                },
                1,
            )
        ]
        quiz = generate_quiz(config)
        self.assertEqual(quiz[0]["question"], "1 / 0")
        self.assertEqual(quiz[0]["answer"], "inf")

    def test_invalid_element_type_raises(self):
        config = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "str", "value": "bad"},
                    ],
                },
                1,
            )
        ]
        with self.assertRaises(ValueError):
            generate_quiz(config)

    def test_generate_quiz_with_float_precision_pattern(self):
        config = [
            (
                {
                    "category": "math",
                    "elements": [
                        {
                            "type": "float.4",
                            "start": 1.123456,
                            "end": 1.123456,
                        },
                        {"type": "operator", "value": "+"},
                        {
                            "type": "float.4",
                            "start": 2.654321,
                            "end": 2.654321,
                        },
                    ],
                },
                1,
            )
        ]
        quiz = generate_quiz(config)
        self.assertEqual(len(quiz), 1)
        question = quiz[0]["question"]
        answer = quiz[0]["answer"]

        self.assertIn("+", question)
        elements = question.split("+")
        self.assertEqual(len(elements), 2)

        left = elements[0].strip()
        right = elements[1].strip()

        self.assertRegex(left, r"\d+\.\d{4}")
        self.assertRegex(right, r"\d+\.\d{4}")

        expected = round(1.1235 + 2.6543, 4)
        self.assertEqual(float(answer), expected)


if __name__ == "__main__":
    unittest.main()