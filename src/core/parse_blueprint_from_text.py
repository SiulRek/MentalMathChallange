import re

from numpy import (
    abs,
    ceil,
    floor,
    round,
    exp,  # noqa: F401
    log,
    log10,
    sqrt,
    sin,
    cos,
    tan,  # noqa: F401
)

from scipy.constants import (
    c,
    h,
    hbar,
    G,
    e,
    k,
    N_A,
    R,
    alpha,
    mu_0,
    epsilon_0,  # noqa: F401
    sigma,
    zero_Celsius,
    pi,
    Avogadro,
    Boltzmann,
    Planck,  # noqa: F401
    speed_of_light,
    elementary_charge,
    gravitational_constant,  # noqa: F401
)

SUPPORTED_OPERATORS = {"+", "-", "*", "/", "//", "%", "**"}


class UserConfigError(Exception):
    """
    Base class for user blueprinturation errors.
    """

    pass


def _parse_tokens_to_kwargs(tokens, keys, type_map):
    assert len(tokens) <= len(keys), "Too many tokens for the provided keys"
    kwargs = {}
    for i, token in enumerate(tokens):
        try:
            kwargs[keys[i]] = type_map[i](token)
        except (ValueError, TypeError) as exc:
            raise UserConfigError(
                f"Invalid token '{token}' for key '{keys[i]}'"
            ) from exc
    return kwargs


def _assert_valid_operators(ops):
    reminder = set(ops) - SUPPORTED_OPERATORS
    if len(ops) == 1:
        msg = f"invalid operator '{ops[0]}'"
    elif len(ops) > 1:
        msg = f"invalid operators '{', '.join(ops)}'"
    assert not reminder, msg


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
    if ignore_constants:
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


def _assert_valid_math_expression_elements(elements, position):

    assert len(elements) > 0, "at least one math element must be defined"

    # Build an example expression
    expr = ""
    for elem in elements:
        if _is_numeric_type(elem["type"], ignore_constants=True):
            expr += "1"
        elif elem["type"] == "operator":
            expr += "*"
        elif elem["type"] in ["bracket", "function", "constant"]:
            expr += elem["value"]
        expr += " " if elem["type"] != "function" else ""

    try:
        float(eval(expr))
    except ZeroDivisionError:
        pass
    except Exception as exc:
        problem = _identify_math_expression_problem(elements)
        msg = (
            f"Invalid math expression at position {position}"
            if position != 1
            else "Invalid math expression"
        )
        if problem:
            msg += ": " + problem
        else:
            msg += ": " + str(exc)
        raise UserConfigError(msg) from exc


def _parse_blueprint_from_text(blueprint_text):
    blueprints = []
    lines = blueprint_text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.lstrip():
            i += 1
            continue
        if line.startswith(" "):
            raise UserConfigError(
                f"Unexpected indentation in blueprint block: '{line}'"
            )

        # Parse the block header
        if ":" not in line:
            raise UserConfigError(f"Invalid blueprint block start: '{line}'")

        try:
            category_element, count_element = line.split(":")
            expr_cat = category_element.strip()
            count = int(count_element.strip())
        except ValueError as exc:
            raise UserConfigError(
                f"Invalid blueprint block start: '{line}'"
            ) from exc

        if expr_cat not in ["math", "date"]:
            raise UserConfigError(f"Invalid blueprint category: '{expr_cat}'")

        expr_blueprint = {"category": expr_cat}
        i += 1

        # Parse the block body
        elements = []
        while i < len(lines) and (lines[i].startswith(" ") or not lines[i]):
            tokens = [token.strip() for token in lines[i].split() if token]
            if not tokens:
                i += 1
                continue

            key = tokens[0]

            if expr_cat == "math":
                if key in ["(", ")"]:
                    assert len(tokens) == 1, f"{key} must have no arguments"
                    elements.append({"type": "bracket", "value": key})
                elif key == "int":
                    assert (
                        1 < len(tokens) <= 3
                    ), "int must have between 1 or 2 arguments"
                    tokens[1:] = tokens[1:][::-1]
                    kwargs = _parse_tokens_to_kwargs(
                        tokens, ["type", "end", "start"], [str, int, int]
                    )
                    elements.append(kwargs)
                elif key == "float" or re.match(r"float\.(\d+)", key):
                    assert (
                        1 < len(tokens) <= 3
                    ), "float must have 1 or 2 arguments"
                    tokens[1:] = tokens[1:][::-1]
                    kwargs = _parse_tokens_to_kwargs(
                        tokens, ["type", "end", "start"], [str, float, float]
                    )
                    elements.append(kwargs)
                elif key == "op":
                    assert len(tokens) > 1, "op must have at least 1 argument"
                    ops = tokens[1:]
                    _assert_valid_operators(ops)
                    val = ops[0] if len(ops) == 1 else ops
                    elements.append({"type": "operator", "value": val})
                elif key == "func":
                    assert (
                        len(tokens) == 2
                    ), "func must have exactly 1 argument"
                    func = tokens[1]
                    _assert_function(func)
                    elements.append({"type": "function", "value": func})
                elif key == "const":
                    msg = "const must have exactly 1 argument"
                    assert len(tokens) == 2, msg
                    const = tokens[1]
                    _assert_constant(const)
                    elements.append({"type": "constant", "value": const})
                else:
                    raise UserConfigError(f"Unknown math sub-key: '{key}'")

            elif expr_cat == "date":
                if key == "start":
                    assert (
                        len(tokens) == 2
                    ), "start must have exactly 1 argument"
                    assert tokens[1].isdigit(), "start must be a number"
                    expr_blueprint["start_year"] = int(tokens[1])
                elif key == "end":
                    assert len(tokens) == 2, "end must have exactly 1 argument"
                    assert tokens[1].isdigit(), "end must be a number"
                    expr_blueprint["end_year"] = int(tokens[1])
                else:
                    raise UserConfigError(f"Unknown date sub-key: '{key}'")

            i += 1

        if expr_cat == "math":
            position = len(blueprints) + 1
            _assert_valid_math_expression_elements(elements, position)
            expr_blueprint["elements"] = elements

        blueprints.append((expr_blueprint, count))

    return blueprints


def parse_blueprint_from_text(blueprint_text):
    """
    Parses a human-friendly blueprint text into structured expression
    blueprints.

    The input text defines one or more blocks. Each block starts with a header
    line of the form:

    <category>: <count>

    - <category>: 'math' or 'date'
    - <count>: number of expressions to generate

    For 'math', the block must include indented lines specifying elements:
        - int [<start>] <end>       # Default start = 0
        - float [<start>] <end>     # Default start = 0.0, precision = 10
        - float.<precision> [<start>] <end>
                                    # Default start = 0.0, e.g., float.2
        - op <operator1> [<...>]    # Valid: + - * / // % **
        - (                         # Open bracket
        - )                         # Close bracket
        - func <function_name>      # Valid: abs, ceil, floor, round,
                                    # exp, log, log10, sqrt, sin, cos,
                                    # tan (uses numpy functions)
        - const <constant_name>     # Valid: c, h, hbar, G, e, k, N_A,
                                    # R, alpha, mu_0, epsilon_0,
                                    # sigma, zero_Celsius, pi,
                                    # Avogadro, Boltzmann, Planck,
                                    # speed_of_light, elementary_charge,
                                    # gravitational_constant
                                    # (uses scipy constants)

    For 'date', valid indented lines include:
        - start <year>              # Optional, default = 1900
        - end <year>                # Optional, default = 2050

    Lines may be indented using spaces or tabs. Blank lines are allowed.
    Malformed input will raise a UserConfigError.

    Parameters
    ----------
    blueprint_text : str
        A string containing one or more indented blueprint blocks. Each block
        describes how to generate expressions of a specified type.

    Returns
    -------
    list of tuple[dict, int]
        A list of (expression_blueprint, count) pairs.

    expression_blueprint : dict Specifies how expressions are generated (Keys
    for optional arguments are allowed to be omitted.):

            - "category": str, one of {"math", "date"}

            If "category" == "math":
                - "elements": list of dicts, each with:
                    - {"type": "int", "start": int, "end": int}
                    - {"type": "float", "start": float, "end": float}
                    - {"type": "float.<precision>", "start": float,
                       "end": float}
                    - {"type": "operator", "value": str or list of str}
                    - {"type": "bracket", "value": "(" or ")"}
                    - {"type": "function", "value": str}
                    - {"type": "constant", "value": str}

            If "category" == "date":
                    - "start_year": int
                    - "end_year": int

    count : int Number of expressions to generate with the given blueprint.

    Raises
    ------
    UserConfigError If the input blueprint text is invalid or
    unsupported.

    """

    try:
        return _parse_blueprint_from_text(blueprint_text)
    except AssertionError as exc:
        raise UserConfigError(f"Invalid blueprint: {exc}") from exc
