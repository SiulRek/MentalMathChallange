import random

from src.core.quiz_parser import evaluate_expression


def generate_quiz(config_text):
    """
    Generate a quiz based on the provided configuration text.

    Parameters
    ----------
    config_text : str
        A string containing the configuration for the quiz. The format is:
        "questions=10, operations=+, -, *, /".

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary contains:
        - "question" : str
            The mathematical expression as a string.
        - "answer" : int or float
            The evaluated result of the expression.
    """
    config = {}
    for part in config_text.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            config[key.strip()] = value.strip()

    try:
        n = int(config.get("questions", 10))
    except ValueError:
        n = 10
    operations = ["+", "-", "*"]
    quiz = []
    for _ in range(n):
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        op = random.choice(operations)
        expr = f"{a} {op} {b}"
        result = evaluate_expression(expr)
        quiz.append({"question": expr, "answer": result})
    return quiz
