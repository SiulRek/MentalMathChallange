def evaluate_expression(expr):
    """
    Evaluate the quiz expression and return the result.

    Parameters
    ----------
    expr : str
        A string containing the expression to be evaluated.

    Returns
    -------
    str
        The result of the evaluated expression as a string.
    """
    try:
        res = eval(expr)
        res = float(res)
    except ZeroDivisionError:
        res = float("inf")
    except (NameError, SyntaxError):
        # Evaluating different expressions
        res = None  # TODO: Change later when processing non-numeric answers required
    return str(res)


def parse_user_answer(user_answer):
    """
    Parse the user's answer and convert it to a float if possible.

    Parameters
    ----------
    user_answer : str
        The user's answer as a string.

    Returns
    -------
    str
        The user's answer as a string. If the answer is a valid float, it is
        converted to a float; otherwise, it remains a string.
    """
    try:
        float(user_answer)
    except ValueError:
        raise  # TODO: Change later when processing non-numeric answers required
    return str(user_answer)
