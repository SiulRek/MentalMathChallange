__all__ = [
    "generate_quiz",
    "compute_quiz_results",
]

from core.main_quiz_engine import MainQuizEngine


def generate_quiz(blueprint):
    """
    Generate a quiz based on the provided blueprint.

    Parameters
    ----------
    blueprint : list of tuple
        A list of tuples where each tuple is (sub_blueprint : dict, count :
        int).

    Returns
    -------
    list
        A list containing generated quiz questions.
    """
    engine = MainQuizEngine()
    return engine.geenrate_quiz(blueprint)


def compute_quiz_results(quiz, user_answers):
    """
    Compute the results of a quiz based on the user's answers.

    Parameters
    ----------
    quiz : list of dict
        A list of dictionaries, where each dictionary contains:
        - "question" : str
            The question text.
        - "user_answers" : str
            The correct answer to the question.
        - "category" : str
            The category of the question, either "date" or "math".
    answers : list of str
        A list of strings representing the user's answers to the quiz questions
        in the same order as the quiz.

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
    engine = MainQuizEngine()
    return engine.compute_quiz_results(quiz, user_answers)
