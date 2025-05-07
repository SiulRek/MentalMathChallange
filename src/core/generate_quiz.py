import random
import re

import numpy as np    # noqa: F401

from src.core.date_utils import random_date, derive_weekday
from src.core.parse_blueprint_from_text import (
    UserConfigError,
    SUPPORTED_OPERATORS,
)

MAX_PRECISION = 10  # Max number of decimal places to retain in the result


def _assert_valid_operators(ops):
    ops = ops if isinstance(ops, list) else [ops]
    for op in ops:
        if op not in SUPPORTED_OPERATORS:
            raise UserConfigError(
                f"Invalid operator '{op}'. Supported operators are: "
                f"{', '.join(SUPPORTED_OPERATORS)}."
            )


def _generate_expression(expr_blueprint):
    if expr_blueprint["category"] == "date":
        start_year = expr_blueprint.get("start_year", 1900)
        end_year = expr_blueprint.get("end_year", 2050)
        assert (
            end_year >= start_year
        ), "End year must be greater or equal to start year"
        return random_date(start_year, end_year), "date"
    if expr_blueprint["category"] == "math":
        elements = expr_blueprint["elements"]
        expr = ""
        for elem in elements:
            elem_type = elem["type"]
            float_precision_match = re.match(r"float\.(\d+)", elem_type)
            if elem_type == "bracket":
                expr += elem["value"]
            elif elem_type in ["int", "float"] or float_precision_match:
                start = elem.get("start", 0)
                end = elem.get("end", None)
                assert (
                    end is not None
                ), "At least 'end' must be defined in 'int/float' range."
                assert (
                    end >= start
                ), "End must be greater or equal to start in int/float"

                if elem_type == "int":
                    expr += str(random.randint(start, end))
                else:
                    prec = (
                        int(float_precision_match.group(1))
                        if float_precision_match
                        else MAX_PRECISION
                    )
                    d = random.uniform(start, end)
                    d = f"{d:.{prec}f}"
                    expr += d.rstrip("0").rstrip(".") if "." in d else d
            elif elem_type == "operator":
                op = elem["value"]
                if isinstance(op, list):
                    op = random.choice(op)
                _assert_valid_operators(op)
                expr += op
            elif elem_type in ["function", "constant"]:
                specifier = elem["value"]
                expr += specifier
            else:
                raise ValueError(
                    f"Invalid element type '{elem['type']}'. Expected "
                    "'int', 'float', or 'operator'."
                )
            expr += " " if elem_type != "function" else ""
        return expr.rstrip(), "math"
    raise ValueError(
        f"Invalid expression category '{expr_blueprint['category']}'. "
        "Expected 'date' or 'math'."
    )


def _prettify_expression(expr, category):
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
    if category == "date":
        year, month, day = expr.split("-")
        month = month_names[int(month) - 1]
        return f"{month} {day}, {year}"
    if category == "math":
        expr = re.sub(r"\(\s+", "(", expr)
        expr = re.sub(r"\s+\)", ")", expr)
    return expr


def _evaluate_expression(expr, category=False):
    if category == "date":
        return derive_weekday(expr)
    # Else category == "math"
    try:
        res = eval(expr)
        float(res)
    except ZeroDivisionError:
        res = float("inf")
    except (ValueError, TypeError, SyntaxError) as e:
        raise ValueError(
            f"Invalid expression '{expr}'. Error: {e}. Expression must be "
            "numeric."
        ) from e
    return str(res)


def generate_quiz(blueprint):
    """
    Generate a quiz based on the provided blueprinturation text.

    Parameters
    ----------
    blueprint : list of tuple (dict, int)
        Defined in src/core/parse_blueprint_from_text.py.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary contains:
        - "question" : str
            The mathematical expression as a string.
        - "answer" : int or float
            The evaluated result of the expression.
        - "category" : str
            The category of the expression, either "date" or "math".
    """
    quiz = []
    for expr_blueprint, n in blueprint:
        for _ in range(n):
            try:
                expr, category = _generate_expression(expr_blueprint)
            except AssertionError as e:
                raise UserConfigError(
                    f"Invalid blueprinturation: {e}"
                )
            answer = _evaluate_expression(expr, category=category)
            expr = _prettify_expression(expr, category=category)
            quiz.append(
                {"question": expr, "answer": answer, "category": category}
            )
    return quiz
