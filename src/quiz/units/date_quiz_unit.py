from quiz.units.date_utils import (
    random_date,
    derive_weekday,
    standardize_weekday_string,
)
from quiz.units.exceptions import UserConfigError, UserResponseError
from quiz.units.quiz_unit_base import QuizUnitBase
from quiz.units.shared import MappingError, map_args_to_option

DEFAULT_START_YEAR = 1900
DEFAULT_END_YEAR = 2050


class DateQuizUnit(QuizUnitBase):
    """
    Quiz unit for generating date-related quizzes, specifically to derive the
    weekday from a random date.
    """

    @classmethod
    def transform_options_to_blueprint_unit(cls, options):
        """
        Convert options to a blueprint unit for the date quiz.
        """
        unit_bp = {}
        try:
            for opt in options:
                key = opt.pop("key")
                args = opt.pop("args")
                if key == "start" and not "start_year" in unit_bp:
                    map_args_to_option(opt, args, [("start_year", int)], 1)
                elif key == "end" and not "end_year" in unit_bp:
                    map_args_to_option(opt, args, [("end_year", int)], 1)
                elif key in ["start", "end"]:
                    raise MappingError(
                        f"Option '{key}' defined multiple times."
                    )
                else:
                    raise UserConfigError(
                        f"Unknown option key: {key}"
                    )
                unit_bp.update(opt)
        except MappingError as e:
            raise UserConfigError(
                f"Invalid option {key}: {e}"
            ) from e
        unit_bp.setdefault("start_year", DEFAULT_START_YEAR)
        unit_bp.setdefault("end_year", DEFAULT_END_YEAR)
        if unit_bp["start_year"] > unit_bp["end_year"]:
            raise UserConfigError(
                "Start year > end year."
            )
        return unit_bp

    @classmethod
    def transform_blueprint_unit_to_options(cls, blueprint_unit):
        """
        Convert a blueprint unit back to options for the date quiz.
        """
        options = []
        options.append(
            {"key": "start", "args": [str(blueprint_unit["start_year"])]}
        )
        options.append(
            {"key": "end", "args": [str(blueprint_unit["end_year"])]}
        )
        return options

    @classmethod
    def _generate_question(cls, blueprint_unit):
        start_year = blueprint_unit["start_year"]
        end_year = blueprint_unit["end_year"]
        return random_date(start_year, end_year)

    @classmethod
    def _envaluate_question(cls, date_str):
        return derive_weekday(date_str)

    @classmethod
    def _prettify_question(cls, date_str):
        year, month, day = date_str.split("-")
        month_names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        month = month_names[int(month) - 1]
        return f"{month} {day}, {year}"

    @classmethod
    def generate_quiz(cls, blueprint_unit):
        count = blueprint_unit["count"]
        quiz = []

        for _ in range(count):
            date = cls._generate_question(blueprint_unit)
            answer = cls._envaluate_question(date)
            question = cls._prettify_question(date)

            quiz.append(
                {"question": question, "answer": answer, "category": "date"}
            )

        return quiz

    @classmethod
    def compare_answers(cls, user_answer, correct_answer):
        return user_answer == correct_answer

    @classmethod
    def parse_user_answer(cls, user_answer):
        try:
            return standardize_weekday_string(user_answer)
        except (AssertionError, ValueError) as e:
            raise UserResponseError(
                str(e)
            ) from e

    @classmethod
    def prettify_answer(cls, answer):
        return answer.capitalize()
