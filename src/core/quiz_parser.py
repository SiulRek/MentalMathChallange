def evaluate_expression(expr):
    try:
        res = eval(expr)
        res = float(res)
    except ZeroDivisionError:
        res = float("inf")
    except (NameError, SyntaxError):
        # Evaluating different expressions
        res = None  # TODO: Change later
    return str(res)


def parse_user_answer(user_answer):
    try:
        user_answer = float(user_answer)
    except ValueError:
        pass
    return str(user_answer)
