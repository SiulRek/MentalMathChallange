import random

from src.core.date_utils import random_date, derive_weekday


def _generate_expression(expr_config):
    if expr_config["type"] == "date":
        start_year = expr_config.get("start_year", 1900)
        end_year = expr_config.get("end_year", 2050)
        assert end_year >= start_year, "End year must be greater or equal to start year"
        return random_date(start_year, end_year), True
    if expr_config["type"] == "math":
        elements = expr_config.get("elements", [])
        assert len(elements) > 0, "At least one element must be defined"
        expr = ""
        for elem in elements:
            if elem["type"] in ["int", "float"]:
                start = elem.get("start", 0)
                end = elem.get("end", None)
                assert end is not None, "At least End must be defined"
                assert end >= start, "End must be greater or equal to start"

                if elem["type"] == "int":
                    expr += str(random.randint(start, end))
                elif elem["type"] == "float":
                    expr += str(random.uniform(start, end))
            elif elem["type"] == "operator":
                op = elem["value"]
                if isinstance(op, list):
                    op = random.choice(op)
                assert op in [
                    "+",
                    "-",
                    "*",
                    "/",
                    "//",
                    "%",
                ], "Operator must be one of +, -, *, /"
                expr += op
            else:
                raise ValueError(
                    f"Invalid element type '{elem['type']}'. Expected "
                    "'int', 'float', or 'operator'."
                )
            expr += " "
        return expr.rstrip(), False
    raise ValueError(
        f"Invalid expression type '{expr_config['type']}'. Expected 'date' "
        "or 'math'."
    )


def _evaluate_expression(expr, is_weekday=False):
    if is_weekday:
        return derive_weekday(expr)
    try:
        res = eval(expr)
        float(res)
    except ZeroDivisionError:
        res = float("inf")
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Invalid expression '{expr}'. Error: {e}. Expression must be " "numeric."
        ) from e
    return str(res)


def generate_quiz(config):
    """
    Generate a quiz based on the provided configuration text.

    Parameters
    ----------
    config : dict
        A dictionary containing the configuration for the quiz. The
        configuration should specify the type of expressions to generate and
        their parameters.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary contains:
        - "question" : str
            The mathematical expression as a string.
        - "answer" : int or float
            The evaluated result of the expression.
        - "is_weekday" : bool
            If True, the expression is treated as a weekday string.
            If False, the expression is treated as a mathematical expression.
    """
    quiz = []
    for expr_config, n in config:
        for _ in range(n):
            expr, is_weekday = _generate_expression(expr_config)
            answer = _evaluate_expression(expr, is_weekday=is_weekday)
            quiz.append(
                {"question": expr, "answer": answer, "is_weekday": is_weekday}
            )
    return quiz
