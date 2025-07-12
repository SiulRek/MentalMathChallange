import unittest

from app.collect_user_answers import collect_user_answers
from quiz import parse_blueprint_from_text, generate_quiz, compute_quiz_results
from tests.utils.base_test_case import BaseTestCase


class QuizIntegrationTest(BaseTestCase):
    def test_full_integration(self):
        # ------------- Test Setup ----------------------
        blueprint_text = [
            """math: 1
  int 1 1
  op +
  int 2 2""",
            """date: 1
  start 2020
  end 2020""",
        ]
        length = len(blueprint_text)
        blueprint_text = "\n\n".join(blueprint_text)

        # --------------- Test Execution -------------------
        parsed = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(parsed)

        # Force specific answers on the quiz for testing purposes, were required
        quiz[1].update({"answer": "monday"})

        submission = {
            "answer_0": "3",
            "answer_1": "Monday",
        }
        user_answers = collect_user_answers(submission, len(quiz))
        results = compute_quiz_results(quiz, user_answers)

        # ------------------ Test Verification -------------------
        self.assertEqual(len(results), length)

        # Verify Math quiz results
        self.assertTrue(results[0]["is_correct"])
        self.assertEqual(results[0]["user_answer"], "3")

        # Verify Date quiz results
        self.assertTrue(results[1]["is_correct"])
        self.assertEqual(results[1]["user_answer"].lower(), "monday")


if __name__ == "__main__":
    unittest.main()
