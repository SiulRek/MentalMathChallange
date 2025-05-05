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


def _parse_user_answer(user_answer, is_weekday=False):
    if not user_answer:
        return
    user_answer = user_answer.strip()
    if is_weekday:
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
            f"Invalid answer '{user_answer}'. Answer must be "
            "numeric."
        ) from e
    user_answer = str(user_answer)
    return user_answer.rstrip("0").rstrip(".") if "." in user_answer else user_answer


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
        - "is_weekday" : bool
            If True, the question is treated as a weekday string.
    submission : dict
        A dictionary containing the user's answers. The keys are expected to be
        in the format "answer_<index>", where <index> is the index of the question
        in the quiz.

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
    quiz = [(q["question"], q["answer"], q["is_weekday"]) for q in quiz]
    results = []
    for quiz_elem, user_answer in zip(quiz, user_answers):
        question, correct_answer, is_weekday = quiz_elem
        user_answer = _parse_user_answer(user_answer, is_weekday)
        if user_answer is None:
            correct = False
        elif is_weekday:
            correct = user_answer == correct_answer
        else:
            correct = (
                correct_answer.startswith(user_answer)
                if len(correct_answer) > len(user_answer)
                else user_answer.startswith(correct_answer)
            )
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
