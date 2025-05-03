import random

from src.core.quiz_parser import evaluate_expression


def generate_quiz(config_text):
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
