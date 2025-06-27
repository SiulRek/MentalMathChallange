from abc import ABC, abstractmethod
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

from core.parse_blueprint_from_text import UserConfigError

MAX_PRECISION = 10


class _QuizGeneratorBase(ABC):
    @classmethod
    @abstractmethod
    def generate(cls, sub_blueprint):
        pass

    @classmethod
    @abstractmethod
    def compare_answer(cls, user_answer, correct_answer):
        pass


class MathQuizGenerator(_QuizGeneratorBase):
    @classmethod
    def _generate_expression(cls, elements):
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
                        "At least 'end' must be defined in 'int/float' range."
                    ) from exc
                assert end >= start, "End must be greater or equal to start"

                if elem_type == "int":
                    expr += str(random.randint(start, end))
                else:
                    prec = (
                        int(float_precision_match.group(1))
                        if float_precision_match else MAX_PRECISION
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
    def _evaluate_expression(cls, expr):
        try:
            res = eval(expr)
            float(res)
        except ZeroDivisionError:
            res = float("inf")
        except (ValueError, TypeError, SyntaxError) as exc:
            raise ValueError(
                f"Invalid expression '{expr}'. Error: {exc}"
            ) from exc
        return str(res)

    @classmethod
    def _prettify_expression(cls, expr):
        expr = re.sub(r"\(\s+", "(", expr)
        expr = re.sub(r"\s+\)", ")", expr)
        return expr

    @classmethod
    def generate(cls, sub_blueprint):
        count = sub_blueprint.get("count", 1)
        quizzes = []

        for _ in range(count):
            elements = sub_blueprint["elements"]
            expr = cls._generate_expression(elements)
            answer = cls._evaluate_expression(expr)
            question = cls._prettify_expression(expr)

            quizzes.append(
                {"question": question, "answer": answer, "category": "math"}
            )

        return quizzes

    @classmethod
    def compare_answer(cls, answer_a, answer_b):
        def adjust_precision(s):
            s = f"{float(s):.{MAX_PRECISION}f}"
            if "." in s:
                exponent = 0
                if "e" in s:
                    s, exponent = s.split("e")
                    exponent = int(exponent)
                s = s.rstrip("0").rstrip(".")
                s = (
                    s + "e" + str(exponent)
                    if exponent != 0 else s
                )
            return s

        def derive_tol(s):
            # Derive a tolerance range based on the least significant decimal
            # digit, scaled by the exponent (if in scientific notation).
            # Examples:
            #   "1.2345"      → 0.0001
            #   "1.23450"     → 0.00001
            #   "1.2345e+2"   → 0.0001 * 10^2 = 0.01
            #   "1000"        → 1
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
