from abc import ABC, abstractmethod

from core.date_utils import (
    random_date,
    derive_weekday,
    sanitize_weekday_string,
)


class _QuizGeneratorBase(ABC):
    @classmethod
    @abstractmethod
    def generate(cls, sub_blueprint):
        pass

    @classmethod
    @abstractmethod
    def compare_answer(cls, user_answer, correct_answer):
        pass


class DateQuizGenerator(_QuizGeneratorBase):
    @classmethod
    def _generate_expression(cls, sub_blueprint):
        start_year = sub_blueprint.get("start_year", 1900)
        end_year = sub_blueprint.get("end_year", 2050)
        assert end_year >= start_year, "End year must be >= start year"
        return random_date(start_year, end_year)

    @classmethod
    def _evaluate_expression(cls, date_str):
        return derive_weekday(date_str)

    @classmethod
    def _prettify_expression(cls, date_str):
        year, month, day = date_str.split("-")
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]
        month = month_names[int(month) - 1]
        return f"{month} {day}, {year}"

    @classmethod
    def generate(cls, sub_blueprint):
        count = sub_blueprint.get("count", 1)
        quizzes = []

        for _ in range(count):
            date = cls._generate_expression(sub_blueprint)
            answer = cls._evaluate_expression(date)
            question = cls._prettify_expression(date)

            quizzes.append(
                {"question": question, "answer": answer, "category": "date"}
            )

        return quizzes

    @classmethod
    def compare_answer(cls, answer_a, answer_b):
        try:
            answer_a = sanitize_weekday_string(answer_a)
            answer_b = sanitize_weekday_string(answer_b)
        except Exception:
            return False
        return answer_a == answer_b
    
    @classmethod
    def prettify_answer(cls, answer):
        return answer.capitalize()
