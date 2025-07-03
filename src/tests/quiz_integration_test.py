import unittest

from app.collect_user_answers import collect_user_answers
from core import parse_blueprint_from_text, generate_quiz, compute_quiz_results
from core.exceptions import UserConfigError, UserResponseError
from tests.utils.base_test_case import BaseTestCase


class QuizIntegrationTest(BaseTestCase):
    def test_full_integration_math_and_date(self):
        blueprint_text = """math: 1
  int 1 1
  op +
  int 2 2

date: 1
  start 2020
  end 2020
"""
        parsed = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(parsed)

        self.assertEqual(len(quiz), 2)

        math_question = quiz[0]
        date_question = quiz[1]

        self.assertIn("question", math_question)
        self.assertIn("answer", math_question)
        self.assertEqual(math_question["category"], "math")

        self.assertEqual(date_question["category"], "date")
        self.assertRegex(date_question["answer"], r"^[A-Za-z]+$")

        submission = {
            "answer_0": "3",
            "answer_1": date_question["answer"],
        }
        user_answers = collect_user_answers(submission, len(quiz))
        results = compute_quiz_results(quiz, user_answers)

        self.assertEqual(len(results), 2)
        self.assertTrue(results[0]["is_correct"])
        self.assertTrue(results[1]["is_correct"])
        self.assertEqual(results[0]["user_answer"], "3")
        self.assertEqual(
            results[1]["user_answer"].lower(), date_question["answer"]
        )

    def test_partial_answers_and_incorrect(self):
        blueprint_text = """math: 2
  int 1 1
  op +
  int 1 1
"""
        parsed = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(parsed)

        submission = {
            "answer_0": "1",
            # answer_1 missing
        }
        user_answers = collect_user_answers(submission, len(quiz))
        # TODO: Fix this test results = compute_quiz_results(quiz, user_answers)

        # self.assertEqual(len(results), 2)
        # self.assertFalse(results[0]["is_correct"])
        # self.assertEqual(results[1]["user_answer"], "Not answered")
        # self.assertFalse(results[1]["is_correct"])

    def test_invalid_user_input_format(self):
        blueprint_text = """math: 1
  int 1 1
  op *
  int 1 1
"""
        parsed = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(parsed)

        submission = {"answer_0": "not_a_number"}
        user_answers = collect_user_answers(submission, len(quiz))

        with self.assertRaises(UserResponseError):
            compute_quiz_results(quiz, user_answers)

    def test_fuzzy_float_answer_check(self):
        blueprint_text = """math: 1
  float 1.0 1.0
  op +
  float 2.0 2.0
"""
        parsed = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(parsed)

        correct = float(quiz[0]["answer"])
        rounded_str = str(round(correct, 1))

        submission = {"answer_0": rounded_str}
        user_answers = collect_user_answers(submission, len(quiz))
        results = compute_quiz_results(quiz, user_answers)
        self.assertTrue(results[0]["is_correct"])

    def test_integration_multiple_operators(self):
        blueprint_text = """math: 1
  int 1 1
  op + - *
  int 2 2
  op /
  int 1 1
"""
        parsed = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(parsed)

        submission = {"answer_0": quiz[0]["answer"]}
        user_answers = collect_user_answers(submission, len(quiz))
        results = compute_quiz_results(quiz, user_answers)
        self.assertTrue(results[0]["is_correct"])

    def test_integration_zero_division(self):
        blueprint_text = """math: 1
  int 1 1
  op /
  int 0 0
"""
        parsed = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(parsed)

        self.assertEqual(quiz[0]["answer"], "inf")
        submission = {"answer_0": "inf"}
        user_answers = collect_user_answers(submission, len(quiz))
        results = compute_quiz_results(quiz, user_answers)
        self.assertTrue(results[0]["is_correct"])

    def test_integration_weekday_case_insensitivity(self):
        blueprint_text = """date: 1
  start 2020
  end 2020
"""
        parsed = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(parsed)

        submission = {"answer_0": quiz[0]["answer"].lower()}
        user_answers = collect_user_answers(submission, len(quiz))
        results = compute_quiz_results(quiz, user_answers)
        self.assertTrue(results[0]["is_correct"])

    def test_integration_float_precision_mismatch(self):
        blueprint_text = """math: 1
  float 1.123456789 1.123456789
  op +
  float 2.987654321 2.987654321
"""
        parsed = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(parsed)

        truncated = str(round(float(quiz[0]["answer"]), 6))
        submission = {"answer_0": truncated}
        user_answers = collect_user_answers(submission, len(quiz))
        results = compute_quiz_results(quiz, user_answers)
        self.assertTrue(results[0]["is_correct"])

    def test_intagration_float_precision_setting(self):
        blueprint_text = """math: 1
  float.2 1.123456789 1.123456789
  op +
  float.3 2.987654321 2.987654321
"""
        parsed = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(parsed)

        self.assertEqual(quiz[0]["question"], "1.12 + 2.988")
        truncated = str(round(float(quiz[0]["answer"]), 3))

        submission = {"answer_0": truncated}
        user_answers = collect_user_answers(submission, len(quiz))
        results = compute_quiz_results(quiz, user_answers)
        self.assertTrue(results[0]["is_correct"])

    def test_integration_invalid_blueprint_rejected(self):
        blueprint_text = """math: 1
  op +
  op -
  op *
"""
        with self.assertRaises(UserConfigError):
            parse_blueprint_from_text(blueprint_text)


if __name__ == "__main__":
    unittest.main()
