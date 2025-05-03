from src.core.quiz_parser import parse_user_answer


def _collect_user_answers(submitted_answers, total_expected_answers):
    def _get_index(item):
        try:
            key = item[0]
        except (ValueError, IndexError):
            raise ValueError(
                f"Invalid answer key '{item[0]}'. Expected format " "'answer_<index>'."
            )
        return int(key.split("_")[1])

    for i in range(total_expected_answers - 1):
        try:
            key = f"answer_{i}"
            if key not in submitted_answers:
                submitted_answers[key] = None
        except (ValueError, IndexError):
            pass
    sorted_form = dict(sorted(submitted_answers.items(), key=_get_index))
    # Expecting form values as answers
    sorted_answers = list(sorted_form.values())
    return sorted_answers


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
    questions, correct_answers = zip(*[(q["question"], q["answer"]) for q in quiz])
    results = []
    for question, correct_answer, user_answer in zip(
        questions, correct_answers, user_answers
    ):
        user_answer = parse_user_answer(user_answer)
        correct = user_answer == correct_answer
        results.append(
            {
                "question": question,
                "correct_answer": correct_answer,
                "user_answer": user_answer or "Not answered",
                "is_correct": correct,
            }
        )
    return results
