from copy import deepcopy
import unittest
from unittest import TestCase
from unittest.mock import patch

from quiz.units.date_quiz_unit import DateQuizUnit
from quiz.units.exceptions import UserConfigError, UserResponseError


class DateQuizTransformOptionsToBlueprintUnitTest(unittest.TestCase):
    def test_valid_start_end_years(self):
        options = [
            {"key": "start", "args": ["2000"]},
            {"key": "end", "args": ["2020"]},
        ]
        blueprint = DateQuizUnit.transform_options_to_blueprint_unit(options)
        self.assertEqual(blueprint["start_year"], 2000)
        self.assertEqual(blueprint["end_year"], 2020)

    def test_default_years(self):
        options = []
        blueprint = DateQuizUnit.transform_options_to_blueprint_unit(options)
        self.assertEqual(blueprint["start_year"], 1900)
        self.assertEqual(blueprint["end_year"], 2050)

    def test_invalid_option_key(self):
        options = [{"key": "unknown", "args": ["2000"]}]
        with self.assertRaises(UserConfigError):
            DateQuizUnit.transform_options_to_blueprint_unit(options)

    def test_duplicate_start_option_key(self):
        options = [
            {"key": "start", "args": ["2000"]},
            {"key": "start", "args": ["2010"]},
        ]
        with self.assertRaises(UserConfigError):
            DateQuizUnit.transform_options_to_blueprint_unit(options)

    def test_duplicate_end_option_key(self):
        options = [
            {"key": "end", "args": ["2020"]},
            {"key": "end", "args": ["2030"]},
        ]
        with self.assertRaises(UserConfigError):
            DateQuizUnit.transform_options_to_blueprint_unit(options)

    def test_start_greater_than_end_year(self):
        options = [
            {"key": "start", "args": ["2025"]},
            {"key": "end", "args": ["2020"]},
        ]
        with self.assertRaises(UserConfigError):
            DateQuizUnit.transform_options_to_blueprint_unit(options)


class DateQuizTransformOptionsToBlueprintTest(unittest.TestCase):
    def test_parse_unparse_roundrip(self):
        options = [
            {"key": "start", "args": ["2020"]},
            {"key": "end", "args": ["2025"]},
        ]
        blueprint = DateQuizUnit.transform_options_to_blueprint_unit(
            deepcopy(options)
        )
        roundtrip = DateQuizUnit.transform_blueprint_unit_to_options(blueprint)
        self.assertEqual(len(roundtrip), 2)
        self.assertEqual(roundtrip, options)


class DateQuizGenerateQuizTest(TestCase):
    def test_generate_quiz(self):
        with patch(
            "quiz.units.date_quiz_unit.random_date"
        ) as mock_random_date:
            mock_random_date.return_value = "2000-01-01"
            blueprint = {"start_year": 2000, "end_year": 2000, "count": 5}
            quiz = DateQuizUnit.generate_quiz(blueprint)
            self.assertEqual(len(quiz), 5)
            for q in quiz:
                self.assertIn("question", q)
                self.assertIn("answer", q)
                self.assertIn("category", q)
                self.assertEqual(q["category"], "date")
                self.assertEqual(q["answer"], "saturday")


class DateQuizParseUserAnswerTest(unittest.TestCase):
    def test_parse_user_answer_valid(self):
        cases = [
            ("Monday", "monday"),
            ("tu", "tuesday"),
            ("WEDNESDAY", "wednesday")
        ]
        for answer, expected in cases:
            answer = DateQuizUnit.parse_user_answer(answer)
            self.assertEqual(answer, expected)

    def test_parse_user_answer_invalid(self):
        answers = [
            "Moonday",
            "t",
            "wednesdayay"
        ]
        for answer in answers:
            with self.assertRaises(UserResponseError):
                DateQuizUnit.parse_user_answer(answer)
            

class DateQuizCompareAnswersTest(unittest.TestCase): 
    def test_compare_answers(self):
        self.assertTrue(DateQuizUnit.compare_answers("monday", "monday"))
        self.assertFalse(DateQuizUnit.compare_answers("monday", "tuesday"))


if __name__ == "__main__":
    unittest.main()
