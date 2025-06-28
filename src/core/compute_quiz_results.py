from core.quiz_engine import QuizEngine


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
    quiz = [(q["question"], q["answer"], q["category"]) for q in quiz]
    results = []
    q_engine = QuizEngine()
    for quiz_elem, user_answer in zip(quiz, user_answers):
        question, correct_answer, category = quiz_elem
        correct_answer = correct_answer.lower()
        q_engine.focus_on_category(category)
        user_answer = q_engine.parse_user_answer(user_answer)
        correct = q_engine.compare_answers(
            user_answer,
            correct_answer,
        )
        user_answer = q_engine.prettify_answer(user_answer)
        correct_answer = q_engine.prettify_answer(correct_answer)
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
