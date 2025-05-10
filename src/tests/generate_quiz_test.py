import unittest

from core.parse_blueprint_from_text import UserConfigError
from core.generate_quiz import generate_quiz
from tests.utils.base_test_case import BaseTestCase


class TestGenerateQuiz(BaseTestCase):

    # ----------- Test Math Quiz Generation --------------
    def test_generate_single_math_quiz_single_value(self):
        blueprint = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "int", "start": 1, "end": 1},
                    ],
                },
                1,
            )
        ]
        quiz = generate_quiz(blueprint)
        self.assertEqual(len(quiz), 1)
        self.assertEqual(quiz[0]["question"], "1")
        self.assertEqual(quiz[0]["answer"], "1")
        self.assertEqual(quiz[0]["category"], "math")

    def test_generate_single_math_quiz_hardcoded(self):
        blueprint = [
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
        quiz = generate_quiz(blueprint)
        self.assertEqual(len(quiz), 1)
        self.assertEqual(quiz[0]["question"], "2 + 3")
        self.assertEqual(quiz[0]["answer"], "5")
        self.assertEqual(quiz[0]["category"], "math")

    def test_generate_multiple_quizzes_fixed_output(self):
        blueprint = [
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
        quiz = generate_quiz(blueprint)
        self.assertEqual(len(quiz), 3)
        for q in quiz:
            self.assertEqual(q["question"], "1 * 5")
            self.assertEqual(q["answer"], "5")
            self.assertEqual(q["category"], "math")

    def test_generate_math_quiz_with_brackets(self):
        blueprint = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "int", "start": 1, "end": 1},
                        {"type": "operator", "value": "+"},
                        {"type": "bracket", "value": "("},
                        {"type": "int", "start": 2, "end": 2},
                        {"type": "operator", "value": "-"},
                        {"type": "int", "start": 3, "end": 3},
                        {"type": "bracket", "value": ")"},
                    ],
                },
                1,
            )
        ]
        quiz = generate_quiz(blueprint)
        self.assertEqual(len(quiz), 1)
        self.assertEqual(quiz[0]["category"], "math")
        self.assertEqual(quiz[0]["question"], "1 + (2 - 3)")
        self.assertEqual(quiz[0]["answer"], "0")

    def test_generate_math_quiz_with_function(self):
        blueprint = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "function", "value": "sin"},
                        {"type": "bracket", "value": "("},
                        {"type": "int", "start": 2, "end": 2},
                        {"type": "bracket", "value": ")"},
                    ],
                },
                1,
            )
        ]
        quiz = generate_quiz(blueprint)
        self.assertEqual(len(quiz), 1)
        self.assertEqual(quiz[0]["category"], "math")
        self.assertEqual(quiz[0]["question"], "sin(2)")
        self.assertEqual(quiz[0]["answer"], "0.9092974268256817")

    def test_generate_math_quiz_with_constant(self):
        blueprint = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "constant", "value": "pi"},
                        {"type": "operator", "value": "+"},
                        {"type": "int", "start": 1, "end": 1},
                    ],
                },
                1,
            )
        ]
        quiz = generate_quiz(blueprint)
        self.assertEqual(len(quiz), 1)
        self.assertEqual(quiz[0]["category"], "math")
        self.assertEqual(quiz[0]["question"], "pi + 1")
        self.assertEqual(quiz[0]["answer"], "4.141592653589793")

    def test_zero_division_handling(self):
        blueprint = [
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
        quiz = generate_quiz(blueprint)
        self.assertEqual(quiz[0]["question"], "1 / 0")
        self.assertEqual(quiz[0]["answer"], "inf")

    def test_generate_quiz_with_float_precision_pattern(self):
        blueprint = [
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
        quiz = generate_quiz(blueprint)
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

    # ----------- Test Date Quiz Generation --------------
    def test_generate_date_question(self):
        blueprint = [
            (
                {"category": "date", "start_year": 2000, "end_year": 2000},
                3,
            )
        ]
        quiz = generate_quiz(blueprint)
        self.assertEqual(len(quiz), 3)
        for q in quiz:
            self.assertEqual(q["category"], "date")
            self.assertRegex(q["question"], r"\w+ \d{2}, \d{4}")
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

    # ----------- Test Default Values -------------------
    def test_default_start_values_for_numerics(self):
        blueprint = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "int", "end": 0},
                        {"type": "operator", "value": "+"},
                        {"type": "float", "end": 0},
                        {"type": "operator", "value": "+"},
                        {"type": "float.3", "end": 0},
                    ],
                },
                3,
            )
        ]
        quiz = generate_quiz(blueprint)
        for q in quiz:
            self.assertEqual(q["category"], "math")
            self.assertEqual(q["question"], "0 + 0 + 0")
            self.assertEqual(q["answer"], "0")

    def test_generate_date_question_with_default_years(self):
        blueprint = [
            (
                {"category": "date"},
                3,
            )
        ]
        quiz = generate_quiz(blueprint)
        self.assertEqual(len(quiz), 3)
        for q in quiz:
            self.assertEqual(q["category"], "date")
            self.assertRegex(q["question"], r"\w+ \d{2}, \d{4}")
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

    # ----------- Test Invalid Cases -------------------
    def test_invalid_math_expr_raises(self):
        blueprint = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "bracket", "value": "("},
                        {"type": "operator", "value": "+"},
                        {"type": "int", "start": 2},
                    ],
                },
                1,
            )
        ]
        with self.assertRaises(UserConfigError):
            generate_quiz(blueprint)

    def test_start_greater_than_end_raises_in_math(self):
        blueprint = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": None, "start": 2, "end": 1},
                    ],
                },
                1,
            )
        ]
        for element_type in ["int", "float", "float.3"]:
            blueprint[0][0]["elements"][0].update({"type": element_type})
            with self.assertRaises(UserConfigError):
                generate_quiz(blueprint)

    def test_start_greater_than_end_raises_in_date(self):
        blueprint = [
            (
                {
                    "category": "date",
                    "start_year": 2000,
                    "end_year": 1999,
                },
                1,
            )
        ]
        with self.assertRaises(UserConfigError):
            generate_quiz(blueprint)

    def test_invalid_expr_type_raises(self):
        blueprint = [({"category": "invalid_type"}, 1)]
        with self.assertRaises(ValueError):
            generate_quiz(blueprint)

    def test_invalid_expr_category_raises(self):
        blueprint = [
            (
                {
                    "category": "math",
                    "elements": [
                        {"type": "int", "start": 1, "end": 1},
                        {"type": "operator", "value": "+"},
                        {"type": "invalid_type"},
                    ],
                },
                1,
            )
        ]
        with self.assertRaises(ValueError):
            generate_quiz(blueprint)


if __name__ == "__main__":
    unittest.main()
