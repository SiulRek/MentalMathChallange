from copy import deepcopy
import unittest

from quiz.units.exceptions import UserConfigError
from quiz.units.memory_quiz_unit import MemoryQuizUnit


class MemoryQuizTransformOptionsToBlueprintUnitTest(unittest.TestCase):
    def test_valid_options(self):
        options = [
            {"key": "fruit", "args": ["apple"]},
            {"key": "color", "args": ["blue"]},
        ]
        blueprint = MemoryQuizUnit.transform_options_to_blueprint_unit(
            options.copy()
        )
        self.assertEqual(len(blueprint["items"]), 2)
        self.assertEqual(blueprint["items"][0]["key"], "fruit")
        self.assertEqual(blueprint["items"][0]["value"], "apple")
        self.assertEqual(blueprint["items"][1]["key"], "color")
        self.assertEqual(blueprint["items"][1]["value"], "blue")

    def test_invalid_option_multiple_args(self):
        options = [{"key": "fruit", "args": ["apple", "banana"]}]
        with self.assertRaises(UserConfigError):
            MemoryQuizUnit.transform_options_to_blueprint_unit(options)

    def test_invalid_option_missing_arg(self):
        options = [{"key": "fruit", "args": []}]
        with self.assertRaises(UserConfigError):
            MemoryQuizUnit.transform_options_to_blueprint_unit(options)


class MemoryQuizTransformBlueprintUnitToOptionsTest(unittest.TestCase):
    def test_conversion_roundtrip(self):
        options = [
            {"key": "fruit", "args": ["apple"]},
            {"key": "color", "args": ["blue"]},
        ]
        blueprint = MemoryQuizUnit.transform_options_to_blueprint_unit(
            options.copy()
        )
        roundtrip = MemoryQuizUnit.transform_blueprint_unit_to_options(
            blueprint
        )
        self.assertEqual(len(roundtrip), 2)
        self.assertEqual(roundtrip[0]["key"], "fruit")
        self.assertEqual(roundtrip[0]["args"], ["apple"])
        self.assertEqual(roundtrip[1]["key"], "color")
        self.assertEqual(roundtrip[1]["args"], ["blue"])


class MemoryQuizGenerateQuizTest(unittest.TestCase):

    def setUp(self):
        self._items = [
            {"key": "capital", "value": "paris"},
            {"key": "animal", "value": "dog"},
        ]
        return super().setUp()

    @property
    def items(self):
        return deepcopy(self._items)

    def _validate_quiz_item(self, q, items):
        keys = [item["key"] for item in items]
        values = [item["value"] for item in items]
        self.assertIn("question", q)
        self.assertIn("answer", q)
        self.assertEqual(q["category"], "memory")
        self.assertTrue(any(key in q["question"] for key in keys))
        self.assertIn(q["answer"], values)

    def test_count_equals_item_length(self):
        blueprint = {
            "count": 2,
            "items": self.items,
        }
        quiz = MemoryQuizUnit.generate_quiz(blueprint)
        self.assertEqual(len(quiz), 2)
        for q in quiz:
            self._validate_quiz_item(q, blueprint["items"])

    def test_count_smaller_than_item_length(self):
        blueprint = {
            "count": 1,
            "items": self.items,
        }
        quiz = MemoryQuizUnit.generate_quiz(blueprint)
        self.assertEqual(len(quiz), 1)
        for q in quiz:
            self._validate_quiz_item(q, blueprint["items"])

    def test_count_greater_than_item_length(self):
        blueprint = {
            "count": 3,
            "items": self.items,
        }
        with self.assertRaises(UserConfigError):
            MemoryQuizUnit.generate_quiz(blueprint)


# Tests for parse_user_answer, compare_answers, and prettify_answer are excluded
# as these methods currently lack unique logic for validation.

if __name__ == "__main__":
    unittest.main()
