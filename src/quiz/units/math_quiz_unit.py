import random
import re

from numpy import (
    abs, ceil, floor, round, exp,   # noqa: F401
    log, log10, sqrt, sin, cos, tan  # noqa: F401
)
from scipy.constants import (
    c, h, hbar, G, e, k, N_A, R, alpha, mu_0, epsilon_0,    # noqa: F401
    sigma, zero_Celsius, pi, Avogadro, Boltzmann, Planck,   # noqa: F401
    speed_of_light, elementary_charge, gravitational_constant   # noqa: F401
)

from quiz.units.exceptions import UserConfigError, UserResponseError
from quiz.units.quiz_unit_base import QuizUnitBase
from quiz.units.shared import MappingError, map_args_to_option

MAX_PRECISION = 10
SUPPORTED_OPERATORS = {"+", "-", "*", "/", "//", "%", "**"}
KEY_MAPPING = {
    "op": "operator",
    "func": "function",
    "const": "constant",
    "(": "bracket",
    ")": "bracket",
}


def _assert_valid_operators(ops):
    reminder = set(ops) - SUPPORTED_OPERATORS
    if len(ops) == 1:
        msg = f"invalid operator '{ops[0]}'"
    elif len(ops) > 1:
        msg = f"invalid operators '{', '.join(ops)}'"
    assert not reminder, msg


def _assert_bracket(bracket):
    assert bracket in ["(", ")"], f"Invalid bracket '{bracket}'"


def _assert_function(func):
    supported = [
        "abs",
        "ceil",
        "floor",
        "round",
        "exp",
        "log",
        "log10",
        "sqrt",
        "sin",
        "cos",
        "tan",
    ]
    assert func in supported, f"Unsupported function '{func}'"


def _assert_constant(const):
    supported = [
        "c",  # speed of light
        "h",  # Planck constant
        "hbar",  # reduced Planck constant
        "G",  # gravitational constant
        "e",  # elementary charge
        "k",  # Boltzmann constant
        "N_A",  # Avogadro's number
        "R",  # gas constant
        "alpha",  # fine-structure constant
        "mu_0",  # vacuum permeability
        "epsilon_0",  # vacuum permittivity
        "sigma",  # Stefan-Boltzmann constant
        "zero_Celsius",  # zero Celsius in Kelvin
        "pi",  # pi
        "Avogadro",  # synonym for N_A
        "Boltzmann",  # synonym for k
        "Planck",  # synonym for h
        "speed_of_light",  # synonym for c
        "elementary_charge",  # synonym for e
        "gravitational_constant",  # synonym for G
    ]
    assert const in supported, f"Unsupported constant '{const}'"


def _is_numeric_type(type_, ignore_constants=False):
    numeric_types = ["int", "float"]
    if not ignore_constants:
        numeric_types += ["constant"]
    return type_ in numeric_types or re.match(r"float\.(\d+)", type_)


def _identify_math_expression_problem(elements):
    # 1. Check for consecutive numeric types
    for i in range(len(elements) - 1):
        if _is_numeric_type(elements[i]["type"]) and _is_numeric_type(
            elements[i + 1]["type"]
        ):
            return "two consecutive numeric types"

    # 2. Check for consecutive operators
    for i in range(len(elements) - 1):
        if (
            elements[i]["type"] == "operator"
            and elements[i + 1]["type"] == "operator"
        ):
            return "two consecutive operators"

    # 3. Check for function not followed by a bracket
    for i in range(len(elements) - 1):
        if elements[i]["type"] == "function":
            if (
                elements[i + 1]["type"] != "bracket"
                or elements[i + 1]["value"] != "("
            ):
                return "function not followed by an opening bracket"

    # 4. Check for bracket never closed or opened
    brackets_counter = 0
    for elem in elements:
        if elem["type"] == "bracket":
            if elem["value"] == "(":
                brackets_counter += 1
            elif elem["value"] == ")":
                brackets_counter -= 1
    if brackets_counter != 0:
        return "unmatched brackets"

    # 5. Check for operator at the beginning (not + or -)
    if elements[0]["type"] == "operator" and elements[0]["value"] not in [
        "-",
        "+",
    ]:
        return "expression starts with an operator"

    # 6. Check for operator or function at the end
    if elements[-1]["type"] in ["operator", "function"]:
        type_ = elements[-1]["type"]
        type_ = "an operator" if type_ == "operator" else "a function"
        return f"expression ends with {type_}"

    # 7. Check for function preceded by a numeric type
    for i in range(len(elements) - 1):
        i = i + 1
        if elements[i]["type"] == "function" and _is_numeric_type(
            elements[i - 1]["type"]
        ):
            return "function preceded by a numeric type"

    return None


def _assert_math_expression_elements(elements):
    assert len(elements) > 0, "at least one math element must be defined"

    # Build an example expression
    expr = ""
    for elem in elements:
        type_ = elem["type"]
        if _is_numeric_type(type_, ignore_constants=True):
            expr += "1"
        elif type_ == "operator":
            value = elem["value"]
            value = list(value) if isinstance(value, str) else value
            _assert_valid_operators(value)
            expr += "*"
        elif type_ in ["bracket", "function", "constant"]:
            if type_ == "bracket":
                _assert_bracket(elem["value"])
            elif type_ == "function":
                _assert_function(elem["value"])
            elif type_ == "constant":
                _assert_constant(elem["value"])
            expr += elem["value"]
        else:
            raise UserConfigError(f"Invalid element type '{type_}'")

        expr += " " if elem["type"] != "function" else ""

    try:
        float(eval(expr))
    except ZeroDivisionError:
        pass
    except Exception as exc:
        problem = _identify_math_expression_problem(elements)
        msg = "Invalid math expression"
        if problem:
            msg += ": " + problem
        else:
            msg += ": " + str(exc)
        raise UserConfigError(msg) from exc


class MathQuizUnit(QuizUnitBase):
    """
    Quiz unit for generating mathematical quizzes based on a blueprint.
    """

    @classmethod
    def generate_blueprint_unit(cls, options):
        """
        Convert options to a blueprint unit for the math quiz.
        """

        def add_opt(opt):
            elems[-1].update(opt)

        blueprint_unit = {"elements": []}
        elems = blueprint_unit["elements"]
        try:
            for opt in options:
                old_key = opt.pop("key")
                key = KEY_MAPPING.get(old_key, old_key)
                elems.append({"type": key})
                args = opt.pop("args")
                if key == "int":
                    args.reverse()
                    map_args_to_option(
                        opt,
                        args,
                        [
                            ("end", int),
                            ("start", int),
                        ],
                        1,
                    )
                    add_opt(opt)
                elif key == "float" or re.match(r"float\.(\d+)", key):
                    args.reverse()
                    map_args_to_option(
                        opt,
                        args,
                        [
                            ("end", float),
                            ("start", float),
                        ],
                        1,
                    )
                    add_opt(opt)
                elif key == "operator":
                    assert (
                        len(args) > 0
                    ), "At least one operator must be defined"
                    args = args[0] if len(args) == 1 else args
                    add_opt({"value": args})
                elif key == "bracket":
                    args = [old_key] + args
                    map_args_to_option(
                        opt,
                        args,
                        [
                            ("value", str),
                        ],
                        1,
                    )
                    add_opt(opt)
                elif key == "function" or key == "constant":
                    map_args_to_option(
                        opt,
                        args,
                        [
                            ("value", str),
                        ],
                        1,
                    )
                    add_opt(opt)
                else:
                    raise UserConfigError(f"Unknown option key: {key}")
        except (MappingError, AssertionError) as e:
            raise UserConfigError(f"Invalid option '{key}': {e}") from e

        if not elems:
            raise UserConfigError(
                "At least one element must be defined in category 'math'."
            )

        try:
            _assert_math_expression_elements(elems)
        except AssertionError as exc:
            raise UserConfigError(f"Invalid math expression: {exc}") from exc

        return blueprint_unit

    @classmethod
    def unparse_options(cls, blueprint_unit):
        """
        Convert a blueprint unit back to options for the math quiz.
        """
        reverse_key_mapping = {v: k for k, v in KEY_MAPPING.items()}
        options = []
        for elem in blueprint_unit["elements"]:
            old_key = elem["type"]
            key = reverse_key_mapping.get(old_key, old_key)
            opt = {"key": key}
            if old_key == "int":
                args = [elem.get("start", 0), elem["end"]]
            elif old_key == "float" or re.match(r"float\.(\d+)", key):
                args = [elem.get("start", 0.0), elem["end"]]
            elif old_key == "operator":
                args = elem["value"]
                if isinstance(args, str):
                    args = [args]
            elif old_key == "bracket":
                opt.update({"key": elem["value"]})
                args = []
            elif old_key in ["function", "constant"]:
                args = [elem["value"]]
            else:
                raise ValueError(f"Invalid element type '{old_key}'")
            args = map(str, args)
            opt.update({"args": args})
            options.append(opt)
        return options

    @classmethod
    def _generate_question(cls, elements):
        expr = ""
        for elem in elements:
            elem_type = elem["type"]
            float_precision_match = re.match(r"float\.(\d+)", elem_type)

            if elem_type == "bracket":
                expr += elem["value"]
            elif elem_type in ["int", "float"] or float_precision_match:
                start = elem.get("start", 0)
                try:
                    end = elem["end"]
                except KeyError as exc:
                    raise UserConfigError(
                        "At least 'end' must be defined in 'int/float' "
                        "range."
                    ) from exc
                assert end >= start, "End must be greater or equal to start"

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
                expr += op
            elif elem_type in ["function", "constant"]:
                expr += elem["value"]
            else:
                raise ValueError(f"Invalid element type '{elem_type}'")
            expr += " " if elem_type != "function" else ""

        return expr.rstrip()

    @classmethod
    def _envaluate_question(cls, expr):
        try:
            res = eval(expr)
            float(res)
        except ZeroDivisionError:
            res = float("inf")
        except (ValueError, TypeError, SyntaxError) as exc:
            raise ValueError(f"Invalid expression '{expr}': {exc}") from exc
        return str(res)

    @classmethod
    def _prettify_question(cls, expr):
        expr = re.sub(r"\(\s+", "(", expr)
        expr = re.sub(r"\s+\)", ")", expr)
        return expr

    @classmethod
    def generate_quiz(cls, blueprint_unit):
        count = blueprint_unit.get("count", 1)
        quiz = []

        for _ in range(count):
            elements = blueprint_unit["elements"]
            expr = cls._generate_question(elements)
            answer = cls._envaluate_question(expr)
            question = cls._prettify_question(expr)

            quiz.append(
                {"question": question, "answer": answer, "category": "math"}
            )

        return quiz

    @classmethod
    def compare_answers(cls, answer_a, answer_b):
        def adjust_precision(s):
            s = f"{float(s):.{MAX_PRECISION}f}"
            if "." in s:
                exponent = 0
                if "e" in s:
                    s, exponent = s.split("e")
                    exponent = int(exponent)
                s = s.rstrip("0").rstrip(".")
                s = s + "e" + str(exponent) if exponent != 0 else s
            return s

        def derive_tol(s):
            # Derive a tolerance range based on the least significant decimal
            # digit, scaled by the exponent (if in scientific notation).
            # Examples: "1.2345"      → 0.0001 "1.23450"     → 0.00001
            # "1.2345e+2"   → 0.0001 * 10^2 = 0.01 "1000"        → 1
            exponent = 0
            if "e" in s:
                s, exponent = s.split("e")
                exponent = int(exponent)
            tol = "".join(["0" if c.isdigit() else c for c in s])
            tol = tol[:-1] + "1"
            return float(tol) * 10**exponent

        if answer_a == answer_b:
            return True

        a = adjust_precision(answer_a)
        b = adjust_precision(answer_b)
        diff = abs(float(a) - float(b))
        tol = max(derive_tol(answer_a), derive_tol(answer_b)) / 2
        return diff <= tol

    @classmethod
    def parse_user_answer(cls, user_answer):
        try:
            float(user_answer)
        except ValueError as e:
            raise UserResponseError(
                f"Invalid answer '{user_answer}'. Answer must be numeric."
            ) from e
        return str(user_answer)

    @classmethod
    def prettify_answer(cls, answer):
        answer = answer.rstrip("0").rstrip(".") if "." in answer else answer
        return answer
