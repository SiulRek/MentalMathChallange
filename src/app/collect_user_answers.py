import warnings


def collect_user_answers(submission, total_expected_answers):
    """
    Collect and sort user answers from a submission dictionary.

    Parameters
    ----------
    submission : dict
        A dictionary containing user answers, where keys are expected to be in
        the format "answer_<index>".
    total_expected_answers : int
        The total number of expected answers.

    Returns
    -------
    list
        Sorted list of user answers with empty strings for missing answers.
    """
    answers = ["" for _ in range(total_expected_answers)]

    for key, value in submission.items():
        if not key.startswith("answer_"):
            continue
        try:
            idx = int(key.split("_", 1)[1])
        except (ValueError, IndexError):
            raise ValueError(
                f"Invalid answer key '{key}'. Expected format "
                "'answer_<index>'."
            )
        if 0 <= idx < total_expected_answers:
            answers[idx] = value
        else:
            warnings.warn(
                f"Index {idx} in key '{key}' is out of range. Ignoring this "
                "answer."
            )
    return answers
