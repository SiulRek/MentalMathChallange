from core.quiz_engine import QuizEngine


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
                                    # exp, log, log10, sqrt, sin, cos, tan (uses
                                    # numpy functions)
        - const <constant_name>     # Valid: c, h, hbar, G, e, k, N_A,
                                    # R, alpha, mu_0, epsilon_0, sigma,
                                    # zero_Celsius, pi, Avogadro, Boltzmann,
                                    # Planck, speed_of_light, elementary_charge,
                                    # gravitational_constant (uses scipy
                                    # constants)

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
    return QuizEngine().parse_blueprint_from_text(blueprint_text)
