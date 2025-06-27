from core.math_quiz_generator import MathQuizGenerator
from core.date_quiz_generator import DateQuizGenerator


def _get_generator(generator_type):
    if generator_type == "math":
        return MathQuizGenerator
    if generator_type == "date":
        return DateQuizGenerator
    raise ValueError(f"Unsupported quiz type: {generator_type}")


def generate_quiz(blueprint):
    quiz = []
    for sub_blueprint, count in blueprint:
        sub_blueprint["count"] = count
        quiz_gen = _get_generator(sub_blueprint["category"])
        quiz.extend(quiz_gen.generate(sub_blueprint))
    return quiz


def compare_answers(answer_a, answer_b, category):
    quiz_gen = _get_generator(category)
    return quiz_gen.compare_answer(answer_a, answer_b)
