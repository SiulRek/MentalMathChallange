from src.core.date_utils import sanitize_weekday_string
from src.core.generate_quiz import MAX_PRECISION


class UserResponseError(Exception):
    """Base class for user answer processing errors."""

    pass


def _collect_user_answers(submitted_answers, total_expected_answers):
    def _get_index(item):
        try:
            key = item[0]
            return int(key.split("_")[1])
        except (ValueError, IndexError):
            raise ValueError(
                f"Invalid answer key '{item[0]}'. Expected format "
                "'answer_<index>'."
            )

    for i in range(total_expected_answers):
        key = f"answer_{i}"
        if key not in submitted_answers:
            submitted_answers[key] = ""

    sorted_form = dict(sorted(submitted_answers.items(), key=_get_index))
    sorted_answers = list(sorted_form.values())
    sorted_answers = [
        str(answer) for answer in sorted_answers
    ]  # XXX: Is this required?
    return sorted_answers


def _parse_user_answer(user_answer, category):
    if not user_answer:
        return
    user_answer = user_answer.strip()
    if category == "date":
        try:
            return sanitize_weekday_string(user_answer)
        except ValueError as e:
            raise UserResponseError(
                f"Invalid weekday string '{user_answer}'. Error: {e}. "
                "Expected one of ['monday', 'tuesday', 'wednesday', "
                "'thursday', 'friday', 'saturday', 'sunday']."
            )
    try:
        user_answer = float(user_answer)
    except ValueError as e:
        raise UserResponseError(
            f"Invalid answer '{user_answer}'. Answer must be numeric."
        ) from e
    user_answer = str(user_answer)
    return (
        user_answer.rstrip("0").rstrip(".")
        if "." in user_answer
        else user_answer
    )


def _truncate_decimal_with_rounding(number_string, decimal_target_length):
    if "." not in number_string:
        raise ValueError("Input must be a decimal number string.")

    integer_str, decimal_str = number_string.split(".")

    if decimal_target_length == 0:
        rounding_digit = int(decimal_str[0]) if len(decimal_str) > 0 else 0
        result = int(integer_str)
        if rounding_digit >= 5:
            result += 1
        return str(result)

    decimal_str = decimal_str.ljust(decimal_target_length + 1, "0")

    trunc_part = decimal_str[:decimal_target_length]
    rounding_digit = int(decimal_str[decimal_target_length])

    if rounding_digit >= 5:
        new_decimal_int = int(trunc_part) + 1
        new_decimal_str = str(new_decimal_int).rjust(
            decimal_target_length, "0"
        )
        if len(new_decimal_str) > decimal_target_length:
            integer_str = str(int(integer_str) + 1)
            new_decimal_str = "0" * decimal_target_length
    else:
        new_decimal_str = trunc_part

    return f"{integer_str}.{new_decimal_str}"


def _compare_numeric_strings(user_answer, correct_answer):
    if not "." in user_answer + correct_answer:
        return user_answer == correct_answer
    if len(user_answer) < len(correct_answer):
        decimal_length = (
            len(user_answer.split(".")[1]) if "." in user_answer else 0
        )
        correct_answer = _truncate_decimal_with_rounding(
            correct_answer, decimal_length
        )
    elif len(user_answer) > len(correct_answer):
        decimal_length = (
            len(correct_answer.split(".")[1]) if "." in correct_answer else 0
        )
        user_answer = _truncate_decimal_with_rounding(
            user_answer, decimal_length
        )
    return user_answer == correct_answer


def compute_quiz_results(quiz, submission):
    """
    Compute the results of a quiz based on the user's answers.

    Parameters
    ----------
    quiz : list of dict
        A list of dictionaries, where each dictionary contains:
        - "question" : str
            The question text.
        - "answer" : str
            The correct answer to the question.
        - "category" : str
            The category of the question, either "date" or "math".
    submission : dict
        A dictionary containing the user's answers. The keys are expected to be
        in the format "answer_<index>", where <index> is the index of the
        question in the quiz.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary contains:
        - "question" : str
            The question text.
        - "correct_answer" : str
            The correct answer to the question.
        - "user_answer" : str
            The user's answer to the question.
        - "is_correct" : bool
            Whether the user's answer is correct.
    """
    user_answers = _collect_user_answers(
        submitted_answers=submission, total_expected_answers=len(quiz)
    )
    quiz = [(q["question"], q["answer"], q["category"]) for q in quiz]
    results = []
    for quiz_elem, user_answer in zip(quiz, user_answers):
        question, correct_answer, category = quiz_elem
        user_answer = _parse_user_answer(user_answer, category)
        if user_answer is None:
            correct = False
        elif category == "date":
            correct = user_answer == correct_answer
        else:
            correct = _compare_numeric_strings(user_answer, correct_answer)
            # Prettify the correct answer
            correct_answer = f"{float(correct_answer):.{MAX_PRECISION}f}"
            correct_answer = (
                correct_answer.rstrip("0").rstrip(".")
                if "." in correct_answer
                else correct_answer
            )
        results.append(
            {
                "question": question,
                "correct_answer": correct_answer,
                "user_answer": user_answer or "Not answered",
                "is_correct": correct,
            }
        )
    return results
