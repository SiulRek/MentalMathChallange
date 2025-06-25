from core.date_utils import sanitize_weekday_string
from core.generate_quiz import MAX_PRECISION


class UserResponseError(Exception):
    """
    Base class for user answer processing errors.
    """

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
    return sorted_answers


def _parse_user_answer(user_answer, category):
    if not user_answer:
        return
    user_answer = user_answer.strip()
    if category == "date":
        try:
            return sanitize_weekday_string(user_answer)
        except (AssertionError, ValueError) as e:
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
    return user_answer


def _adjust_numeric_precision(correct_answer, precision):
    correct_answer = f"{float(correct_answer):.{precision}f}"
    if "." in correct_answer:
        exponent = 0
        if "e" in correct_answer:
            correct_answer, exponent = correct_answer.split("e")
            exponent = int(exponent)
        correct_answer = correct_answer.rstrip("0").rstrip(".")
        correct_answer = (
            correct_answer + "e" + str(exponent)
            if exponent != 0
            else correct_answer
        )
    return correct_answer


def _derive_tolerance_range(numeric_string):
    # Derive a tolerance range based on the least significant decimal digit,
    # scaled by the exponent (if in scientific notation).
    # Examples:
    #   "1.2345"      → 0.0001
    #   "1.23450"     → 0.00001
    #   "1.2345e+2"   → 0.0001 * 10^2 = 0.01
    #   "1000"        → 1

    exponent = 0
    if "e" in numeric_string:
        numeric_string, exponent = numeric_string.split("e")
    tolerance_mask = "".join(
        ["0" if c.isdigit() else c for c in numeric_string]
    )
    tolerance_mask = tolerance_mask[:-1] + "1"
    range = float(tolerance_mask) * 10 ** int(exponent)
    return range


def _tolerant_comparison_of_numeric_strings(a, b):
    if a == "in" or b == "inf":
        return a == b
    tol_range_a = _derive_tolerance_range(a)
    tol_range_b = _derive_tolerance_range(b)
    diff = abs(float(a) - float(b))
    if tol_range_a == tol_range_b:
        return diff == 0
    return diff < max(tol_range_a, tol_range_b) / 2


def _remove_trailing_zeros(numeric_string):
    numeric_string = (
        numeric_string.rstrip("0").rstrip(".")
        if "." in numeric_string
        else numeric_string
    )

    return numeric_string


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
        - "category" : str
            The category of the question, either "date" or "math".
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
        correct_answer = correct_answer.lower()
        user_answer = _parse_user_answer(user_answer, category)
        if user_answer is None:
            correct = False
        elif category == "date":
            correct = user_answer == correct_answer
            user_answer = user_answer.capitalize()
            correct_answer = correct_answer.capitalize()
        else:
            correct_answer = _adjust_numeric_precision(
                correct_answer, MAX_PRECISION
            )
            user_answer = _adjust_numeric_precision(user_answer, MAX_PRECISION)
            correct = _tolerant_comparison_of_numeric_strings(
                user_answer, correct_answer
            )
            correct_answer = _remove_trailing_zeros(correct_answer)
            user_answer = _remove_trailing_zeros(user_answer)
        results.append(
            {
                "question": question,
                "category": category,
                "correct_answer": correct_answer,
                "user_answer": user_answer or "Not answered",
                "is_correct": correct,
            }
        )
    return results
