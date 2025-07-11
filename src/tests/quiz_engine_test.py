from copy import deepcopy
import unittest
from unittest.mock import patch

from quiz.quiz_engine import QuizEngine
from quiz.units.exceptions import UserConfigError
from quiz.units.quiz_unit_base import QuizUnitBase
from tests.utils.base_test_case import BaseTestCase


class DummyQuizUnit(QuizUnitBase):
    @classmethod
    def transform_options_to_blueprint_unit(cls, options):
        return {"value": "dummy"}

    @classmethod
    def transform_blueprint_unit_to_options(cls, blueprint_unit):
        return [{"key": "dummy_option", "args": ["dummy_arg"]}]

    @classmethod
    def generate_quiz(cls, blueprint_unit):
        return [{"question": "2+2?", "answer": "4", "category": "DUMMY"}]

    @classmethod
    def parse_user_answer(cls, user_answer):
        return user_answer.strip()

    @classmethod
    def compare_answers(cls, user_answer, correct_answer):
        return user_answer == correct_answer

    @classmethod
    def prettify_answer(cls, answer):
        return answer


old_mapping = "quiz.quiz_engine.QUIZ_UNIT_MAPPING"
new_mapping = {"DUMMY": DummyQuizUnit}


@patch(old_mapping, new_mapping)
class ParseBlueprintFromTextTest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.engine = QuizEngine()
        self.std_blueprint_text = "DUMMY: 2\n  dummy_option dummy_arg\n"

    def _tranform_function_spy(self):
        return patch.object(
            DummyQuizUnit,
            "transform_options_to_blueprint_unit",
            wraps=DummyQuizUnit.transform_options_to_blueprint_unit,
        )

    def _assert_unit_in_blueprint(self, blueprint):
        for unit, category in blueprint:
            self.assertEqual(unit["count"], 2)
            self.assertEqual(unit["value"], "dummy")
            self.assertEqual(category, "DUMMY")

    def _assert_transform_call_args(self, func_spy):
        if isinstance(func_spy, unittest.mock._Call):
            called_args = func_spy[0][0]
        else:
            called_args = func_spy.call_args[0][0]
        self.assertEqual(
            called_args, [{"key": "dummy_option", "args": ["dummy_arg"]}]
        )

    def test_one_blueprint_unit(self):
        with self._tranform_function_spy() as spy:
            blueprint = self.engine.parse_blueprint_from_text(
                self.std_blueprint_text
            )

            self.assertEqual(len(blueprint), 1)
            self._assert_unit_in_blueprint(blueprint)

            spy.assert_called_once()
            self._assert_transform_call_args(spy)

    def test_multiple_blueprint_units(self):
        blueprint_text = self.std_blueprint_text
        blueprint_text = "\n".join([blueprint_text] * 3)
        with self._tranform_function_spy() as spy:
            blueprint = self.engine.parse_blueprint_from_text(blueprint_text)

            self.assertEqual(len(blueprint), 3)
            self._assert_unit_in_blueprint(blueprint)

            self.assertEqual(spy.call_count, 3)
            for call in spy.call_args_list:
                self._assert_transform_call_args(call)

    def test_unnecessary_blank_lines(self):
        blueprint_text = self.std_blueprint_text.replace("\n", "\n\n")
        blueprint_text = "\n" + blueprint_text + "\n"
        with self._tranform_function_spy() as spy:
            blueprint = self.engine.parse_blueprint_from_text(blueprint_text)

            self.assertEqual(len(blueprint), 1)
            self._assert_unit_in_blueprint(blueprint)
            spy.assert_called_once()
            self._assert_transform_call_args(spy)

    def test_unnecessary_spaces(self):
        blueprint_text = self.std_blueprint_text.replace(" ", "  ")
        blueprint_text = blueprint_text.replace("\n", "\n ")
        blueprint_text = blueprint_text.replace(":", " :")
        with self._tranform_function_spy() as spy:
            blueprint = self.engine.parse_blueprint_from_text(blueprint_text)

            self.assertEqual(len(blueprint), 1)
            self._assert_unit_in_blueprint(blueprint)
            spy.assert_called_once()
            self._assert_transform_call_args(spy)

    def test_no_options(self):
        blueprint_text = "DUMMY: 1\n"
        with self._tranform_function_spy() as spy:
            blueprint = self.engine.parse_blueprint_from_text(blueprint_text)

            self.assertEqual(len(blueprint), 1)
            self.assertEqual(blueprint[0][0]["count"], 1)
            self.assertEqual(blueprint[0][0]["value"], "dummy")
            self.assertEqual(blueprint[0][1], "DUMMY")
            spy.assert_called_once()
            called_args = spy.call_args[0][0]
            self.assertEqual(called_args, [])

    def test_invalid_block_start(self):
        cases = [
            "DUMMY \n  dummy_option dummy_arg\n",
            "DUMMY 1\n  dummy_option dummy_arg\n",
            "DUMMY: one\n  dummy_option dummy_arg\n",
            "DUMMY: 1 2\n  dummy_option dummy_arg\n",
        ]
        for blueprint_text in cases:
            with self.assertRaises(UserConfigError):
                self.engine.parse_blueprint_from_text(blueprint_text)

    def test_unknown_category(self):
        blueprint_text = "UNKNOWN: 1\n  dummy_option dummy_arg\n"
        with self.assertRaises(UserConfigError):
            self.engine.parse_blueprint_from_text(blueprint_text)

    def test_invalid_count(self):
        cases = [
            "DUMMY: 0\n  dummy_option dummy_arg\n",
            "DUMMY: -1\n  dummy_option dummy_arg\n",
            "DUMMY: 1.5\n  dummy_option dummy_arg\n",
        ]
        for blueprint_text in cases:
            with self.assertRaises(UserConfigError):
                self.engine.parse_blueprint_from_text(blueprint_text)

    def test_unexpected_indentation(self):
        blueprint_text = "  DUMMY: 1\n dummy_option dummy_arg\n"
        with self.assertRaises(UserConfigError):
            self.engine.parse_blueprint_from_text(blueprint_text)

    def test_missing_indentation(self):
        blueprint_text = "DUMMY: 1\ndummy_option dummy_arg\n"
        with self.assertRaises(UserConfigError):
            self.engine.parse_blueprint_from_text(blueprint_text)


@patch(old_mapping, new_mapping)
class UnparseBlueprintToTextTest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.engine = QuizEngine()
        self._blueprint = [({"count": 2, "value": "dummy"}, "DUMMY")]

    @property
    def blueprint(self):
        return deepcopy(self._blueprint)

    def test_transform_blueprint_unit_to_options_called_correctly(self):
        with patch.object(
            DummyQuizUnit,
            "transform_blueprint_unit_to_options",
            wraps=DummyQuizUnit.transform_blueprint_unit_to_options,
        ) as spy:
            text = self.engine.unparse_blueprint_to_text(self.blueprint)
            self.assertEqual(text, "DUMMY: 2\n  dummy_option dummy_arg")
            expected_call = self.blueprint[0][0]
            expected_call.pop("count")
            spy.assert_called_once_with(expected_call)

    def test_unparse_one_blueprint_unit(self):
        text = self.engine.unparse_blueprint_to_text(self.blueprint)
        expected = "DUMMY: 2\n  dummy_option dummy_arg"
        self.assertEqual(text, expected)

    def test_unparse_multiple_blueprint_units(self):
        # Create three independent copies of self.blueprint using manual
        # addition instead of repeating references with self.blueprint * 3
        blueprint = self.blueprint + self.blueprint + self.blueprint
        text = self.engine.unparse_blueprint_to_text(blueprint)
        expected = "\n\n".join(["DUMMY: 2\n  dummy_option dummy_arg"] * 3)
        self.assertEqual(text, expected)

    def test_unparse_no_options(self):
        with patch.object(DummyQuizUnit, "transform_blueprint_unit_to_options", return_value=[]):
            blueprint = [({"count": 1, "value": "dummy"}, "DUMMY")]
            text = self.engine.unparse_blueprint_to_text(blueprint)
            expected = "DUMMY: 1"
            self.assertEqual(text, expected)

    def test_unparse_multiple_options(self):
        blueprint = [
            ({"count": 2, "value": "dummy"}, "DUMMY"),
            ({"count": 3, "value": "dummy"}, "DUMMY"),
        ]
        text = self.engine.unparse_blueprint_to_text(blueprint)
        expected = (
            "DUMMY: 2\n  dummy_option dummy_arg\n\n"
            "DUMMY: 3\n  dummy_option dummy_arg"
        )
        self.assertEqual(text, expected)


@patch(old_mapping, new_mapping)
class GenerateQuizTest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.engine = QuizEngine()
        self.blueprint = [({"count": 1, "value": "dummy"}, "DUMMY")]

    def test_generate_quiz_called_correctly(self):
        with patch.object(
            DummyQuizUnit,
            "generate_quiz",
            wraps=DummyQuizUnit.generate_quiz,
        ) as spy:
            quiz = self.engine.generate_quiz(self.blueprint)
            self.assertEqual(len(quiz), 1)
            self.assertEqual(quiz[0]["question"], "2+2?")
            self.assertEqual(quiz[0]["answer"], "4")
            self.assertEqual(quiz[0]["category"], "DUMMY")
            spy.assert_called_once_with(self.blueprint[0][0])

    def test_generate_quiz_single_question(self):
        quiz = self.engine.generate_quiz(self.blueprint)
        self.assertEqual(len(quiz), 1)
        self.assertEqual(quiz[0]["question"], "2+2?")
        self.assertEqual(quiz[0]["answer"], "4")
        self.assertEqual(quiz[0]["category"], "DUMMY")

    def test_generate_quiz_multiple_questions(self):
        blueprint = self.blueprint * 3
        quiz = self.engine.generate_quiz(blueprint)
        self.assertEqual(len(quiz), 3)
        for q in quiz:
            self.assertEqual(q["question"], "2+2?")
            self.assertEqual(q["answer"], "4")
            self.assertEqual(q["category"], "DUMMY")


@patch(old_mapping, new_mapping)
class ComputeQuizResultsTest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.engine = QuizEngine()
        self.quiz = [{"question": "2+2?", "answer": "4", "category": "DUMMY"}]

    def test_internal_function_called_correctly(self):
        with patch.object(
            DummyQuizUnit,
            "parse_user_answer",
            wraps=DummyQuizUnit.parse_user_answer,
        ) as parse_spy, patch.object(
            DummyQuizUnit,
            "compare_answers",
            wraps=DummyQuizUnit.compare_answers,
        ) as compare_spy, patch.object(
            DummyQuizUnit,
            "prettify_answer",
            wraps=DummyQuizUnit.prettify_answer,
        ) as prettify_spy:
            user_answers = ["4"]
            results = self.engine.compute_quiz_results(self.quiz, user_answers)

            parse_spy.assert_called_once_with("4")
            compare_spy.assert_called_once_with("4", "4")
            prettify_spy.assert_called_with("4")
            self.assertEqual(len(results), 1)

    def test_compute_correct_result(self):
        user_answers = ["4"]
        results = self.engine.compute_quiz_results(self.quiz, user_answers)
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result["question"], "2+2?")
        self.assertEqual(result["category"], "DUMMY")
        self.assertEqual(result["correct_answer"], "4")
        self.assertEqual(result["user_answer"], "4")
        self.assertTrue(result["is_correct"])

    def test_compute_incorrect_result(self):
        user_answers = ["5"]
        results = self.engine.compute_quiz_results(self.quiz, user_answers)
        self.assertFalse(results[0]["is_correct"])
        self.assertEqual(results[0]["user_answer"], "5")

    def test_compute_not_answered(self):
        user_answers = [""]
        results = self.engine.compute_quiz_results(self.quiz, user_answers)
        self.assertFalse(results[0]["is_correct"])
        self.assertEqual(results[0]["user_answer"], "Not answered")


if __name__ == "__main__":
    unittest.main()
