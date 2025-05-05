class UserConfigError(Exception):
    """Base class for user configuration errors."""

    pass


def _parse_tokens_to_kwargs(tokens, keys, type_map):
    assert len(tokens) <= len(keys), "Too many tokens for the provided keys"
    kwargs = {}
    for i, token in enumerate(tokens):
        kwargs[keys[i]] = type_map[i](token)
    return kwargs


def _assert_valid_operators(ops):
    reminder = set(ops) - {"+", "-", "*", "/", "//", "%"}
    assert not reminder, f"Invalid operator(s): {reminder}"


def _assert_valid_math_expression_elements(elements):
    assert len(elements) > 0, "At least one element must be defined"
    assert elements[0]["type"] in [
        "int",
        "float",
    ], f"First element must be of type int or float, but got {elements[0]['type']}"
    assert elements[-1]["type"] in [
        "int",
        "float",
    ], f"Last element must be of type int or float, but got {elements[-1]['type']}"
    for i in range(1, len(elements) - 1):
        i_is_numeric = elements[i]["type"] in ["int", "float"]
        i_plus_1_is_numeric = elements[i + 1]["type"] in ["int", "float"]
        assert i_is_numeric != i_plus_1_is_numeric, (
            f"Element {i} and {i + 1} must be of different types, but both are "
            f"{elements[i]['type']}"
        )


def _parse_config_from_text(config_text):
    configs = []
    lines = config_text.strip().splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Parse the block header
        if ":" not in line:
            raise UserConfigError(
                f"Invalid config block start: '{line}'"
            )

        try:
            type_part, count_part = line.split(":")
            expr_type = type_part.strip()
            count = int(count_part.strip())
        except ValueError as e:
            raise UserConfigError(
                f"Invalid config block start: '{line}'"
            ) from e
        expr_config = {"type": expr_type}
        i += 1

        # Parse the block body
        elements = []
        while i < len(lines) and (lines[i].startswith(" ") or not lines[i]):
            tokens = [token.strip() for token in lines[i].split() if token]
            if not tokens:
                i += 1
                continue

            key = tokens[0]

            if expr_type == "math":
                if key == "int":
                    assert (
                        1 < len(tokens) <= 3
                    ), "int must have between 2 and 3 arguments"
                    tokens[1:] = tokens[1:][::-1]
                    kwargs = _parse_tokens_to_kwargs(
                        tokens, ["type", "end", "start"], [str, int, int]
                    )
                    elements.append(kwargs)
                elif key == "float":
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

            elif expr_type == "date":
                if key == "start":
                    assert len(tokens) == 2, "start must have exactly 1 argument"
                    assert tokens[1].isdigit(), "start must be a number"
                    expr_config["start_year"] = int(tokens[1])
                elif key == "end":
                    assert len(tokens) == 2, "end must have exactly 1 argument"
                    assert tokens[1].isdigit(), "end must be a number"
                    expr_config["end_year"] = int(tokens[1])
                else:
                    raise UserConfigError(
                        f"Unknown date sub-key: '{key}'"
                    )

            else:
                raise UserConfigError(
                    f"Unknown expression type: '{expr_type}'"
                )

            i += 1

        if expr_type == "math":
            _assert_valid_math_expression_elements(elements)
            expr_config["elements"] = elements

        configs.append((expr_config, count))

    return configs


def parse_config_from_text(config_text):
    """
    Parses human-friendly configuration text into structured expression configs.

    Supported Syntax:
    - Each block starts with a header line in the form: '<type>: <count>'
        - <type>: 'math' or 'date'
        - <count>: number of expressions to generate
    - The lines that follow (indented) define the configuration parameters:
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
    config_text : str
        A string representation of the configuration written in a concise,
        human-friendly format, as described above.

    Returns
    -------
    list of tuple
        A list of (expression_config, count) pairs, where:
        expression_config : dict
            Specifies the expression generation rules. Must include:
            - "type" : {"date", "math"}
              - If "type" == "date":
                  Optional:
                      - "start_year" : int, default=1900
                      - "end_year" : int, default=2050
              - If "type" == "math":
                  - "elements" : list of dict
                      - "type" : {"int", "float", "operator"}
                          - If "int" or "float":
                              - "start" : int or float
                              - "end" : int or float
                          - If "operator":
                              - "value" : str or list of str, one or more of
                                {"+", "-", "*", "/", "//", "%"}
        count : int
            The number of expressions to generate with the given config.
    """
    try:
        return _parse_config_from_text(config_text)
    except AssertionError as e:
        raise UserConfigError(
            f"Invalid configuration: {e}"
        )
