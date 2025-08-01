import random

from quiz.units.exceptions import UserConfigError
from quiz.units.quiz_unit_base import QuizUnitBase


def _assert_valid_key(key):
    # Must be alphanumeric including underscores
    assert key.isidentifier(), "key must be a valid identifier"
    pass


def _assert_valid_value(value):
    # No specific validation for value, but can be extended
    pass


class MemoryQuizUnit(QuizUnitBase):
    """
    Quiz unit for generating memory-related quizzes based on a blueprint.
    """

    @classmethod
    def transform_options_to_blueprint_unit(cls, options):
        """
        Convert options to a blueprint unit for the memory quiz.
        """
        items = []
        unit_bp = {"items": items}
        try:
            for opt in options:
                key = opt.pop("key")
                args = opt.pop("args")
                assert len(args) in (
                    1,
                    2,
                ), "only one or two arguments are allowed"
                value = args[0]
                if len(args) == 2:
                    status = args[1].lower()
                    assert status in [
                        "off",
                        "on",
                    ], "second argument must be 'off' or 'on'"
                    enable = status == "on"
                else:
                    enable = True
                _assert_valid_key(key)
                _assert_valid_value(value)
                items.append({"key": key, "value": value, "enable": enable})
        except AssertionError as e:
            raise UserConfigError(
                f"Invalid option '{key}': {e}"
            ) from e
        return unit_bp

    @classmethod
    def transform_blueprint_unit_to_options(cls, blueprint_unit):
        """
        Convert a blueprint unit back to options for the memory quiz.
        """
        options = []
        for item in blueprint_unit["items"]:
            args = [item["value"]]
            args += ["on" if item["enable"] else "off"]
            options.append({"key": item["key"], "args": args})
        return options

    @classmethod
    def generate_quiz(cls, blueprint_unit):
        """
        Generate a quiz question based on the blueprint unit.
        """
        count = blueprint_unit["count"]

        items = [
            (item["key"], item["value"])
            for item in blueprint_unit["items"]
            if item["enable"]
        ]
        if not items or len(items) < count:
            raise UserConfigError(
                "Not enough enabled items to generate the quiz"
            )
        selected_items = random.sample(items, count)

        quiz = []
        for item in selected_items:
            name, value = item
            question = f"What is the value of '{name}'?"
            quiz.append(
                {
                    "question": question,
                    "answer": value,
                    "category": "memory",
                }
            )
        return quiz

    @classmethod
    def parse_user_answer(cls, user_answer):
        return str(user_answer)

    @classmethod
    def compare_answers(cls, user_answer, correct_answer):
        """
        Compare the user's answer with the correct answer.
        """
        return user_answer == correct_answer

    @classmethod
    def prettify_answer(cls, answer):
        return answer
