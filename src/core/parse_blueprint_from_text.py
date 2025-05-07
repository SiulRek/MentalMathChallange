import re


from numpy import (
    abs, ceil, floor, round, exp, log, log10, sqrt, sin, cos, tan  # noqa: F401
)
from scipy.constants import (
    c, h, hbar, G, e, k, N_A, R, alpha, mu_0, epsilon_0,    # noqa: F401
    sigma, zero_Celsius, pi, Avogadro, Boltzmann, Planck,   # noqa: F401
    speed_of_light, elementary_charge, gravitational_constant   # noqa: F401
)

SUPPORTED_OPERATORS = {"+", "-", "*", "/", "//", "%", "**"}

class UserConfigError(Exception):
    """Base class for user blueprinturation errors."""

    pass


def _parse_tokens_to_kwargs(tokens, keys, type_map):
    assert len(tokens) <= len(keys), "Too many tokens for the provided keys"
    kwargs = {}
    for i, token in enumerate(tokens):
        kwargs[keys[i]] = type_map[i](token)
    return kwargs

def _map_to_np_function_str(func):
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
    if func not in supported:
        raise UserConfigError(
            f"Unsupported function '{func}'"
        )
    return f"{func}"

def _map_to_scipy_constant_str(const):
    supported = [
        "c",                # speed of light
        "h",                # Planck constant
        "hbar",             # reduced Planck constant
        "G",                # gravitational constant
        "e",                # elementary charge
        "k",                # Boltzmann constant
        "N_A",              # Avogadro's number
        "R",                # gas constant
        "alpha",            # fine-structure constant
        "mu_0",             # vacuum permeability
        "epsilon_0",        # vacuum permittivity
        "sigma",            # Stefan-Boltzmann constant
        "zero_Celsius",     # zero Celsius in Kelvin
        "pi",               # pi
        "Avogadro",         # synonym for N_A
        "Boltzmann",        # synonym for k
        "Planck",           # synonym for h
        "speed_of_light",   # synonym for c
        "elementary_charge",# synonym for e
        "gravitational_constant" # synonym for G
    ]
    if const not in supported:
        raise UserConfigError(
            f"Unsupported constant '{const}'"
        )
    value = eval(const)
    return f"{value}"


def _assert_valid_operators(ops):
    reminder = set(ops) - SUPPORTED_OPERATORS
    assert not reminder, f"Invalid operator(s): {reminder}"


def _assert_valid_math_expression_elements(elements, position):
    def _is_numeric_type(type_):
        return type_ in ["int", "float"] or re.match(r"float\.(\d+)", type_)

    assert len(elements) > 0, "At least one element must be defined"

    # Build an example expression
    expr = ""
    for elem in elements:
        if _is_numeric_type(elem["type"]):
            expr += "1"
        elif elem["type"] == "operator":
            expr += "*"
        elif elem["type"] == "bracket":
            expr += elem["value"]
        elif elem["type"] == "constant":
            expr += elem["value"]
        expr += " "

    try:
        eval(expr)
    except ZeroDivisionError:
        pass
    except Exception as exp:
        raise UserConfigError(
            "Unable to construct a valid math expression for the blueprint "
            f"at position {position}."
        ) from exp


def _parse_blueprint_from_text(blueprint_text):
    blueprints = []
    lines = blueprint_text.strip().splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Parse the block header
        if ":" not in line:
            raise UserConfigError(
                f"Invalid blueprint block start: '{line}'"
            )

        try:
            category_element, count_element = line.split(":")
            expr_cat = category_element.strip()
            count = int(count_element.strip())
        except ValueError as exp:
            raise UserConfigError(
                f"Invalid blueprint block start: '{line}'"
            ) from exp
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
                    ), "int must have between 2 and 3 arguments"
                    tokens[1:] = tokens[1:][::-1]
                    kwargs = _parse_tokens_to_kwargs(
                        tokens, ["type", "end", "start"], [str, int, int]
                    )
                    elements.append(kwargs)
                elif key == "float" or re.match(r"float\.(\d+)", key):
                    assert (
                        1 < len(tokens) <= 3
                    ), "float must have 2 or 3 arguments"
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
                    assert len(tokens) == 2, "func must have exactly 1 argument"
                    name = tokens[1]
                    func_str = _map_to_np_function_str(name)
                    elements.append({"type": "function", "value": func_str})
                elif key == "const":
                    msg = "const must have exactly 1 argument"
                    assert len(tokens) == 2, msg
                    const = tokens[1]
                    const_str = _map_to_scipy_constant_str(const)
                    elements.append({"type": "constant", "value": const_str})
                else:
                    raise UserConfigError(
                        f"Unknown math sub-key: '{key}'"
                    )

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
                    raise UserConfigError(
                        f"Unknown date sub-key: '{key}'"
                    )

            else:
                raise UserConfigError(
                    f"Unknown expression type: '{expr_cat}'"
                )

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

    The input text defines one or more blocks. Each block starts with a
    header line of the form:

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
        A string containing one or more indented blueprint blocks. Each
        block describes how to generate expressions of a specified type.

    Returns
    -------
    list of tuple[dict, int]
        A list of (expression_blueprint, count) pairs.

        expression_blueprint : dict
            Specifies how expressions are generated
            (Keys for optional arguments are allowed to be omitted.):

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

        count : int
            Number of expressions to generate with the given blueprint.


    Raises
    ------
    UserConfigError
        If the input blueprint text is invalid or unsupported.
    """

    try:
        return _parse_blueprint_from_text(blueprint_text)
    except AssertionError as exp:
        raise UserConfigError(
            f"Invalid blueprinturation: {exp}"
        ) from exp
