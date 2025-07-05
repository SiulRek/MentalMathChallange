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
SUPPORTED_FUNCTIONS = {
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
}
SUPPORTED_CONSTANTS = {
    "c",
    "h",
    "hbar",
    "G",
    "e",
    "k",
    "N_A",
    "R",
    "alpha",
    "mu_0",
    "epsilon_0",
    "sigma",
    "zero_Celsius",
    "pi",
    "Avogadro",
    "Boltzmann",
    "Planck",
    "speed_of_light",
    "elementary_charge",
    "gravitational_constant",
}

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
    assert func in SUPPORTED_FUNCTIONS, f"Unsupported function '{func}'"


def _assert_constant(const):
    assert const in SUPPORTED_CONSTANTS, f"Unsupported constant '{const}'"


def _is_numeric_type(type_, ignore_constants=False):
    numeric_types = ["int", "float"]
    if not ignore_constants:
        numeric_types += ["constant"]
    return type_ in numeric_types or re.match(r"float\.(\d+)", type_)


def _identify_math_expression_problem(elements):
    for i in range(len(elements) - 1):
        if _is_numeric_type(elements[i]["type"]) and _is_numeric_type(
            elements[i + 1]["type"]
        ):
            return "two consecutive numeric types"

    for i in range(len(elements) - 1):
        if (
            elements[i]["type"] == "operator"
            and elements[i + 1]["type"] == "operator"
        ):
            return "two consecutive operators"

    for i in range(len(elements) - 1):
        if elements[i]["type"] == "function":
            if (
                elements[i + 1]["type"] != "bracket"
                or elements[i + 1]["value"] != "("
            ):
                return "function not followed by an opening bracket"

    brackets_counter = 0
    for elem in elements:
        if elem["type"] == "bracket":
            if elem["value"] == "(":
                brackets_counter += 1
            elif elem["value"] == ")":
                brackets_counter -= 1
        if brackets_counter < 0:
            return "bracket closed without opening"
    if brackets_counter != 0:
        return "unmatched brackets"

    if elements[0]["type"] == "operator" and elements[0]["value"] not in [
        "-",
        "+",
    ]:
        return "expression starts with an operator"

    if elements[-1]["type"] in ["operator", "function"]:
        type_ = elements[-1]["type"]
        type_ = "an operator" if type_ == "operator" else "a function"
        return f"expression ends with {type_}"

    for i in range(len(elements) - 1):
        i = i + 1
        if elements[i]["type"] == "function" and _is_numeric_type(
            elements[i - 1]["type"]
        ):
            return "function preceded by numeric"

    return None


def _assert_math_expression_elements(elements):
    assert len(elements) > 0, "at least one math element must be defined"

    expr = ""
    for elem in elements:
        type_ = elem["type"]
        if _is_numeric_type(type_, ignore_constants=True):
            start, end = elem["start"], elem["end"]
            assert end >= start, f"{end} not greater or equal to {start}"
            expr += "1" if not type_.startswith("float") else "1.0"
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
    def _maybe_convert_constant_option(cls, opt):
        val = opt["value"]
        if val.isnumeric():
            type_ = "int"
            val = int(val)
        else:
            try:
                val = float(val)
                type_ = "float"
            except ValueError:
                return
        opt.clear()
        opt.update({"type": type_, "start": val, "end": val})

    @classmethod
    def transform_options_to_blueprint_unit(cls, options):
        """
        Convert options to a blueprint unit for the math quiz.
        """
        blueprint_unit = {"elements": []}
        elems = blueprint_unit["elements"]
        try:
            for opt in options:
                old_key = opt.pop("key")
                key = KEY_MAPPING.get(old_key, old_key)
                opt.update({"type": key})
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
                elif key == "operator":
                    assert (
                        len(args) > 0
                    ), "At least one operator must be defined"
                    opt.update({"value": args})
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
                elif key == "function" or key == "constant":
                    map_args_to_option(
                        opt,
                        args,
                        [
                            ("value", str),
                        ],
                        1,
                    )
                else:
                    raise UserConfigError(f"Unknown option key: {key}")

                if _is_numeric_type(key, ignore_constants=True):
                    opt.setdefault("start", 0)

                if opt["type"] == "constant":
                    cls._maybe_convert_constant_option(opt)

                elems.append(opt)

        except (MappingError, AssertionError) as e:
            raise UserConfigError(f"Invalid option '{key}': {e}") from e

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
                args = [elem["start"], elem["end"]]
            elif old_key == "float" or re.match(r"float\.(\d+)", key):
                args = [elem["start"], elem["end"]]
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
            args = list(map(str, args))
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
                start = elem["start"]
                end = elem["end"]

                if elem_type == "int":
                    expr += str(random.randint(start, end))
                else:
                    prec = (
                        int(float_precision_match.group(1))
                        if float_precision_match
                        else MAX_PRECISION
                    )
                    d = random.uniform(start, end)
                    expr += f"{d:.{prec}f}"

            elif elem_type == "operator":
                op = elem["value"]
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
            res = float("nan")
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
            exponent = 0
            if "e" in s:
                s, exponent = s.split("e")
                exponent = int(exponent)
            tol = "".join(["0" if c.isdigit() else c for c in s])
            tol = tol[:-1] + "1"
            return float(tol) * 10**exponent

        if answer_a == answer_b:
            return True

        if "nan" in (answer_a, answer_b):
            return False

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