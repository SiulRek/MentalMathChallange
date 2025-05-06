import re

SUPPORTED_OPERATORS = {"+", "-", "*", "/", "//", "%"}


class UserConfigError(Exception):
    """Base class for user blueprinturation errors."""

    pass


def _parse_tokens_to_kwargs(tokens, keys, type_map):
    assert len(tokens) <= len(keys), "Too many tokens for the provided keys"
    kwargs = {}
    for i, token in enumerate(tokens):
        kwargs[keys[i]] = type_map[i](token)
    return kwargs


def _assert_valid_operators(ops):
    reminder = set(ops) - SUPPORTED_OPERATORS
    assert not reminder, f"Invalid operator(s): {reminder}"


def _assert_valid_math_expression_elements(elements):
    def _is_numeric_type(type_):
        return type_ in ["int", "float"] or re.match(r"float\.(\d+)", type_)
    
    assert len(elements) > 0, "At least one element must be defined"
    assert _is_numeric_type(elements[0]["type"]), (
        "First element must be of type int or float, but got "
        f"{elements[0]['type']}"
    )
    assert _is_numeric_type(elements[-1]["type"]), (
        "Last element must be of type int or float, but got "
        f"{elements[-1]['type']}"
    )
    for i in range(1, len(elements) - 1):
        i_is_numeric = _is_numeric_type(elements[i]["type"])
        i_plus_1_is_numeric = _is_numeric_type(elements[i + 1]["type"])
        assert i_is_numeric != i_plus_1_is_numeric, (
            f"Element {i} and {i + 1} must be of different types, but both are "
            f"{elements[i]['type']}"
        )


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
        except ValueError as e:
            raise UserConfigError(
                f"Invalid blueprint block start: '{line}'"
            ) from e
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
                if key == "int":
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
            _assert_valid_math_expression_elements(elements)
            expr_blueprint["elements"] = elements

        blueprints.append((expr_blueprint, count))

    return blueprints


def parse_blueprint_from_text(blueprint_text):
    """
    Parses human-friendly blueprinturation text into structured expression
    blueprints.

    Supported Syntax:
    - Each block starts with a header line in the form: '<type>: <count>'
        - <type>: 'math' or 'date'
        - <count>: number of expressions to generate
    - The lines that follow (indented) define the blueprinturation parameters:
        For math:
          - int <start> <end>
          - float <start> <end>
          - op <+ - * / // %>
        For date:
          - start <year>
          - end <year>
    - Blocks are separated by empty lines.

    Example:
        math: 3
          int 1 10
          op + -
          int 5 15

        date: 2
          start 2000
          end 2020

    Parameters
    ----------
    blueprint_text : str
        A string representation of the blueprinturation written in a concise,
        human-friendly format, as described above.

    Returns
    -------
    list of tuple
        A list of (expression_blueprint, count) pairs, where:
        expression_blueprint : dict
            Specifies the expression generation rules. Must include:
            - "category" : {"date", "math"}
              - If "category" == "date":
                      - "start_year" : int (optional, default=1900)
                      - "end_year" : int (optional, default=2050)
              - If "category" == "math":
                  - "elements" : list of dict
                      - "type" : {"int", "float", "operator"}
                          - If "int" or "float":
                              - "start" : int or float (optional, default 0)
                              - "end" : int or float
                          - If "operator":
                              - "value" : str or list of str, one or more of
                                {"+", "-", "*", "/", "//", "%"}
        count : int
            The number of expressions to generate with the given blueprint.
    """
    try:
        return _parse_blueprint_from_text(blueprint_text)
    except AssertionError as e:
        raise UserConfigError(
            f"Invalid blueprinturation: {e}"
        )
