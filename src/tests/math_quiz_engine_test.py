import unittest
from unittest.mock import patch

from core.exceptions import UserResponseError
from core.math_quiz_engine import MathQuizEngine
from core.exceptions import UserConfigError
from tests.utils.base_test_case import BaseTestCase


@patch("core.math_quiz_engine.MAX_PRECISION", 10)
class MathQuizGeneratorTest(BaseTestCase):

    # ---------------- Test generate method ----------------
    def test_generate_single_int(self):
        blueprint = {
            "elements": [{"type": "int", "start": 1, "end": 1}],
            "count": 1,
        }
        result = MathQuizEngine.generate(blueprint)
        quiz = result[0]
        self.assertEqual(quiz["question"], "1")
        self.assertEqual(quiz["answer"], "1")

    def test_generate_expression_simple_add(self):
        blueprint = {
            "elements": [
                {"type": "int", "start": 2, "end": 2},
                {"type": "operator", "value": "+"},
                {"type": "int", "start": 3, "end": 3},
            ],
            "count": 1,
        }
        result = MathQuizEngine.generate(blueprint)
        quiz = result[0]
        self.assertEqual(quiz["question"], "2 + 3")
        self.assertEqual(quiz["answer"], "5")

    def test_generate_multiple_quizzes_fixed_output(self):
        blueprint = {
            "elements": [
                {"type": "int", "start": 1, "end": 1},
                {"type": "operator", "value": "*"},
                {"type": "int", "start": 5, "end": 5},
            ],
            "count": 3,
        }
        result = MathQuizEngine.generate(blueprint)
        self.assertEqual(len(result), 3)
        for quiz in result:
            self.assertEqual(quiz["question"], "1 * 5")
            self.assertEqual(quiz["answer"], "5")

    def test_generate_with_brackets(self):
        blueprint = {
            "elements": [
                {"type": "int", "start": 1, "end": 1},
                {"type": "operator", "value": "+"},
                {"type": "bracket", "value": "("},
                {"type": "int", "start": 2, "end": 2},
                {"type": "operator", "value": "-"},
                {"type": "int", "start": 3, "end": 3},
                {"type": "bracket", "value": ")"},
            ],
            "count": 1,
        }
        result = MathQuizEngine.generate(blueprint)
        quiz = result[0]
        self.assertEqual(quiz["question"], "1 + (2 - 3)")
        self.assertEqual(quiz["answer"], "0")

    def test_generate_with_constant(self):
        blueprint = {
            "elements": [
                {"type": "constant", "value": "pi"},
                {"type": "operator", "value": "+"},
                {"type": "int", "start": 1, "end": 1},
            ],
            "count": 1,
        }
        result = MathQuizEngine.generate(blueprint)
        quiz = result[0]
        self.assertEqual(quiz["question"], "pi + 1")
        self.assertAlmostEqual(
            float(quiz["answer"]), 3.141592653589793 + 1, places=5
        )

    def test_generate_with_float_precision_pattern(self):
        blueprint = {
            "elements": [
                {"type": "float.4", "start": 1.123456, "end": 1.123456},
                {"type": "operator", "value": "+"},
                {"type": "float.4", "start": 2.654321, "end": 2.654321},
            ],
            "count": 1,
        }
        result = MathQuizEngine.generate(blueprint)
        quiz = result[0]
        parts = quiz["question"].split("+")
        self.assertEqual(len(parts), 2)
        self.assertRegex(parts[0].strip(), r"\d+\.\d{4}")
        self.assertRegex(parts[1].strip(), r"\d+\.\d{4}")
        self.assertAlmostEqual(
            float(quiz["answer"]), 1.1235 + 2.6543, places=4
        )

    def test_default_start_values(self):
        blueprint = {
            "elements": [
                {"type": "int", "end": 0},
                {"type": "operator", "value": "+"},
                {"type": "float", "end": 0},
                {"type": "operator", "value": "+"},
                {"type": "float.3", "end": 0},
            ],
            "count": 1,
        }
        result = MathQuizEngine.generate(blueprint)
        quiz = result[0]
        self.assertEqual(quiz["question"], "0 + 0 + 0")
        self.assertEqual(quiz["answer"], "0")

    def test_zero_division_handling(self):
        blueprint = {
            "elements": [
                {"type": "int", "start": 1, "end": 1},
                {"type": "operator", "value": "/"},
                {"type": "int", "start": 0, "end": 0},
            ],
            "count": 1,
        }
        result = MathQuizEngine.generate(blueprint)
        self.assertEqual(result[0]["answer"], "inf")

    def test_invalid_element_type_raises(self):
        blueprint = {
            "elements": [{"type": "unknown", "value": "x"}],
            "count": 1,
        }
        with self.assertRaises(ValueError):
            MathQuizEngine.generate(blueprint)

    def test_start_greater_than_end_raises(self):
        for element_type in ["int", "float", "float.3"]:
            blueprint = {
                "elements": [{"type": element_type, "start": 2, "end": 1}],
                "count": 1,
            }
            with self.assertRaises(AssertionError):
                MathQuizEngine.generate(blueprint)

    def test_missing_end_raises_user_config_error(self):
        blueprint = {
            "elements": [{"type": "float", "start": 0}],
            "count": 1,
        }
        with self.assertRaises(UserConfigError):
            MathQuizEngine.generate(blueprint)

    # ---------------- Test compare_answers method ----------------
    def test_compare_answers_exact_and_tolerance(self):
        equal_numbers = [
            ("1.0", "1.00"),
            ("1.5", "1.50"),
            ("0.0001", "1e-4"),
            ("0.00011", "1e-4"),
            ("1000", "1e3"),
            ("999", "1e3"),
            ("2", "1.99"),
            ("0.0001", "0.9e-4"),
        ]
        for a, b in equal_numbers:
            with self.subTest(a=a, b=b):
                self.assertTrue(MathQuizEngine.compare_answers(a, b))
                self.assertTrue(MathQuizEngine.compare_answers(b, a))

        not_equal_numbers = [
            ("1.1", "1.0001"),
            ("1.5", "1.59"),
            ("1.5e-8", "1.5e-9"),
        ]
        for a, b in not_equal_numbers:
            with self.subTest(a=a, b=b):
                self.assertFalse(MathQuizEngine.compare_answers(a, b))
                self.assertFalse(MathQuizEngine.compare_answers(b, a))

    def test_compare_answers_incorrect(self):
        self.assertFalse(MathQuizEngine.compare_answers("5", "2"))

    # ---------------- Test parse_user_answer method ----------------
    def test_parse_user_answer_valid(self):
        valid_answers = [
            "1.0",
            "2.5",
            "3.1400",
            "4.0000",
            "5.1234567890",
            "1e3",
            "2.0001",
        ]
        for answer in valid_answers:
            with self.subTest(answer=answer):
                self.assertEqual(
                    MathQuizEngine.parse_user_answer(answer), answer
                )

    def test_parse_user_answer_invalid(self):
        invalid_answers = [
            "abc",
            "1.2.3",
            "1e",
            "1e+",
            "1e-",
            "1.2e3.4",
            "1.2e3+4",
        ]
        for answer in invalid_answers:
            with self.subTest(answer=answer):
                with self.assertRaises(UserResponseError):
                    MathQuizEngine.parse_user_answer(answer)

    # ---------------- Test prettify_answer method ----------------
    def test_prettify_answer(self):
        test_cases = [
            ("1.0000", "1"),
            ("2.5000", "2.5"),
            ("3.1400", "3.14"),
            ("4.0000", "4"),
            ("5.1234567890", "5.123456789"),
        ]
        for input_val, expected in test_cases:
            with self.subTest(input_val=input_val, expected=expected):
                self.assertEqual(
                    MathQuizEngine.prettify_answer(input_val), expected
                )


if __name__ == "__main__":
    unittest.main()
