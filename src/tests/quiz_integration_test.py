import unittest

from src.core.compute_quiz_results import (
    compute_quiz_results,
    UserResponseError,
)
from src.core.generate_quiz import generate_quiz
from src.core.parse_config_from_text import _parse_config_from_text
from src.tests.utils.base_test_case import BaseTestCase


class TestQuizIntegration(BaseTestCase):

    def test_full_integration_math_and_date(self):
        config_text = """math: 1
  int 1 1
  op +
  int 2 2

date: 1
  start 2020
  end 2020
"""
        parsed = _parse_config_from_text(config_text)
        quiz = generate_quiz(parsed)

        self.assertEqual(len(quiz), 2)

        math_question = quiz[0]
        date_question = quiz[1]

        self.assertIn("question", math_question)
        self.assertIn("answer", math_question)
        self.assertFalse(math_question["is_weekday"])

        self.assertTrue(date_question["is_weekday"])
        self.assertRegex(date_question["answer"], r"^[A-Za-z]+$")

        user_answers = {
            "answer_0": "3",
            "answer_1": date_question["answer"],
        }

        results = compute_quiz_results(quiz, user_answers)

        self.assertEqual(len(results), 2)
        self.assertTrue(results[0]["is_correct"])
        self.assertTrue(results[1]["is_correct"])
        self.assertEqual(results[0]["user_answer"], "3")
        self.assertEqual(results[1]["user_answer"], date_question["answer"])

    def test_partial_answers_and_incorrect(self):
        config_text = """math: 2
  int 1 1
  op +
  int 1 1
"""
        parsed = _parse_config_from_text(config_text)
        quiz = generate_quiz(parsed)

        user_answers = {
            "answer_0": "1",
        }

        results = compute_quiz_results(quiz, user_answers)

        self.assertEqual(len(results), 2)
        self.assertFalse(results[0]["is_correct"])
        self.assertEqual(results[1]["user_answer"], "Not answered")
        self.assertFalse(results[1]["is_correct"])

    def test_invalid_user_input_format(self):
        config_text = """math: 1
  int 1 1
  op *
  int 1 1
"""
        parsed = _parse_config_from_text(config_text)
        quiz = generate_quiz(parsed)

        user_answers = {"answer_0": "not_a_number"}

        with self.assertRaises(UserResponseError):
            compute_quiz_results(quiz, user_answers)

    def test_fuzzy_float_answer_check(self):
        config_text = """math: 1
  float 1.0 1.0
  op +
  float 2.0 2.0
"""
        parsed = _parse_config_from_text(config_text)
        quiz = generate_quiz(parsed)

        correct = float(quiz[0]["answer"])
        rounded_str = str(round(correct, 1))

        user_answers = {"answer_0": rounded_str}

        results = compute_quiz_results(quiz, user_answers)
        self.assertTrue(results[0]["is_correct"])

    def test_integration_multiple_operators(self):
        config_text = """math: 1
  int 1 1
  op + - *
  int 2 2
  op /
  int 1 1
"""
        parsed = _parse_config_from_text(config_text)
        quiz = generate_quiz(parsed)
        user_answers = {"answer_0": quiz[0]["answer"]}
        results = compute_quiz_results(quiz, user_answers)
        self.assertTrue(results[0]["is_correct"])

    def test_integration_zero_division(self):
        config_text = """math: 1
  int 1 1
  op /
  int 0 0
"""
        parsed = _parse_config_from_text(config_text)
        quiz = generate_quiz(parsed)
        self.assertEqual(quiz[0]["answer"], "inf")
        user_answers = {"answer_0": "inf"}
        results = compute_quiz_results(quiz, user_answers)
        self.assertTrue(results[0]["is_correct"])

    def test_integration_weekday_case_insensitivity(self):
        config_text = """date: 1
  start 2020
  end 2020
"""
        parsed = _parse_config_from_text(config_text)
        quiz = generate_quiz(parsed)
        user_answers = {"answer_0": quiz[0]["answer"].lower()}
        results = compute_quiz_results(quiz, user_answers)
        self.assertTrue(results[0]["is_correct"])

    def test_integration_float_precision_mismatch(self):
        config_text = """math: 1
  float 1.123456789 1.123456789
  op +
  float 2.987654321 2.987654321
"""
        parsed = _parse_config_from_text(config_text)
        quiz = generate_quiz(parsed)
        truncated = str(round(float(quiz[0]["answer"]), 6))
        user_answers = {"answer_0": truncated}
        results = compute_quiz_results(quiz, user_answers)
        self.assertTrue(results[0]["is_correct"])

    def test_integration_invalid_config_rejected(self):
        config_text = """math: 1
  op +
  op -
  op *
"""
        with self.assertRaises(AssertionError):
            _parse_config_from_text(config_text)


if __name__ == "__main__":
    unittest.main()