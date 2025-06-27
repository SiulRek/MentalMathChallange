from core.date_quiz_generator import DateQuizGenerator
from core.math_quiz_generator import MathQuizGenerator


def _get_generator(generator_type):
    if generator_type == "math":
        return MathQuizGenerator
    if generator_type == "date":
        return DateQuizGenerator
    raise ValueError(
        f"Unsupported quiz type: {generator_type}"
    )


def generate_quiz(blueprint):
    quiz = []
    for sub_blueprint, count in blueprint:
        sub_blueprint["count"] = count
        quiz_gen = _get_generator(sub_blueprint["category"])
        quiz.extend(quiz_gen.generate(sub_blueprint))
    return quiz


def compare_answers(answer_a, answer_b, category):
    if not answer_a or not answer_b:
        return False
    quiz_gen = _get_generator(category)
    return quiz_gen.compare_answer(answer_a, answer_b)


def parse_user_answer(user_answer, category):
    try:
        user_answer = user_answer.strip()
    except AttributeError:
        pass
    if not user_answer:
        return None

    quiz_gen = _get_generator(category)
    return quiz_gen.parse_user_answer(user_answer)


def prettify_answer(answer, category):
    if not answer:
        return None
    quiz_gen = _get_generator(category)
    return quiz_gen.prettify_answer(answer)
