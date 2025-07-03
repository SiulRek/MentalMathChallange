from core.units.date_utils import (
    random_date,
    derive_weekday,
    standardize_weekday_string,
)
from core.units.exceptions import UserConfigError, UserResponseError
from core.units.quiz_unit_base import QuizUnitBase
from core.units.shared import MappingError, map_args_to_option


class DateQuizUnit(QuizUnitBase):
    """
    Quiz unit for generating date-related quizzes, specifically to derive the
    weekday from a random date.
    """

    @classmethod
    def generate_blueprint_unit(cls, options):
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

        # Test if blueprint unit can generate a quiz
        cls._generate_question(unit_bp)

        return unit_bp

    @classmethod
    def _generate_question(cls, unit_blueprint):
        start_year = unit_blueprint.get("start_year", 1900)
        end_year = unit_blueprint.get("end_year", 2050)
        assert end_year >= start_year, "End year must be >= start year"
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
    def generate_quiz(cls, unit_blueprint):
        count = unit_blueprint.get("count", 1)
        quiz = []

        for _ in range(count):
            date = cls._generate_question(unit_blueprint)
            answer = cls._envaluate_question(date)
            question = cls._prettify_question(date)

            quiz.append(
                {"question": question, "answer": answer, "category": "date"}
            )

        return quiz

    @classmethod
    def compare_answers(cls, answer_a, answer_b):
        try:
            answer_a = standardize_weekday_string(answer_a)
            answer_b = standardize_weekday_string(answer_b)
        except Exception:
            return False
        return answer_a == answer_b

    @classmethod
    def parse_user_answer(cls, user_answer):
        try:
            return standardize_weekday_string(user_answer)
        except (AssertionError, ValueError) as e:
            # TODO: Remove line 75 to 76 of error message
            raise UserResponseError(
                f"Invalid weekday string "
            ) from e

    @classmethod
    def prettify_answer(cls, answer):
        return answer.capitalize()
