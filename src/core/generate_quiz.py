import random
import re

from src.core.date_utils import random_date, derive_weekday
from src.core.parse_config_from_text import UserConfigError, SUPPORTED_OPERATORS

MAX_PRECISION = 10  # Max number of decimal places to retain in the result


def _assert_valid_operators(ops):
    ops = ops if isinstance(ops, list) else [ops]
    for op in ops:
        if op not in SUPPORTED_OPERATORS:
            raise UserConfigError(
                f"Invalid operator '{op}'. Supported operators are: "
                f"{', '.join(SUPPORTED_OPERATORS)}."
            )


def _generate_expression(expr_config):
    if expr_config["category"] == "date":
        start_year = expr_config.get("start_year", 1900)
        end_year = expr_config.get("end_year", 2050)
        assert end_year >= start_year, (
            "End year must be greater or equal to start year"
        )
        return random_date(start_year, end_year), True
    if expr_config["category"] == "math":
        elements = expr_config["elements"]
        expr = ""
        for elem in elements:
            type_ = elem["type"]
            float_precision_match = re.match(r"float\.(\d+)", type_)
            if elem["type"] in ["int", "float"] or float_precision_match:
                start = elem.get("start", 0)
                end = elem.get("end", None)
                assert end is not None, (
                    "At least 'end' must be defined in 'int/float' range."
                )
                assert (
                    end >= start
                ), "End must be greater or equal to start in int/float"

                if elem["type"] == "int":
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
            elif elem["type"] == "operator":
                op = elem["value"]
                if isinstance(op, list):
                    op = random.choice(op)
                _assert_valid_operators(op)
                expr += op
            else:
                raise ValueError(
                    f"Invalid element type '{elem['type']}'. Expected "
                    "'int', 'float', or 'operator'."
                )
            expr += " "
        return expr.rstrip(), False
    raise ValueError(
        f"Invalid expression category '{expr_config['category']}'. Expected 'date' "
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
    except (ValueError, TypeError, SyntaxError) as e:
        raise ValueError(
            f"Invalid expression '{expr}'. Error: {e}. "
            "Expression must be numeric."
        ) from e
    return str(res)


def generate_quiz(config):
    """
    Generate a quiz based on the provided configuration text.

    Parameters
    ----------
    config : list of tuple (dict, int)
        A list of (expression_config, count) pairs, where:
        - expression_config : dict
            Specifies the expression generation rules. Must include:
            - "category": str, one of {"date", "math"}.
              - If "category" == "date":
                  Optional:
                    - "start_year": int (default=1900)
                    - "end_year": int (default=2050)
              - If "category" == "math":
                  - "elements": list of dicts, each with:
                      - "type": str, one of:
                        {"int", "float", "operator", "float.<precision>"}
                          - If "int" or "float":
                              - "start": int or float
                              - "end": int or float
                          - If "float.<precision>":
                              - Precision can be set manually after "float." 
                                (e.g., "float.3" for 3 decimal places).
                              - "start": float
                              - "end": float
                          - If "operator":
                              - "value": str or list of str, one or more of
                                {"+", "-", "*", "/", "//", "%"}
        - count : int
            The number of expressions to generate with the given config.

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
            try:
                expr, is_weekday = _generate_expression(expr_config)
            except AssertionError as e:
                raise UserConfigError(f"Invalid configuration: {e}")
            answer = _evaluate_expression(expr, is_weekday=is_weekday)
            quiz.append({"question": expr, "answer": answer, "is_weekday": is_weekday})
    return quiz
