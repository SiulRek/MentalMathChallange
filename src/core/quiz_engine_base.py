from abc import ABC, abstractmethod


class QuizEngineBase(ABC):
    @classmethod
    @abstractmethod
    def generate(cls, sub_blueprint):
        """
        Generate a quiz based on the provided sub_blueprint.
        """
        pass

    @classmethod
    @abstractmethod
    def parse_user_answer(cls, user_answer):
        """
        Parse the user's answer and return it in a standardized format.
        """
        pass

    @classmethod
    @abstractmethod
    def compare_answers(cls, answer_a, answer_b):
        """
        Compare two answers and return True if they are equivalent, False
        otherwise.
        """

        pass

    @classmethod
    @abstractmethod
    def prettify_answer(cls, answer):
        """
        Prettify the answer for display purposes.
        """

        pass
    
    @classmethod
    def compute_quiz_results(cls, quiz, user_answers):
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
        if not hasattr(cls, "focus_on_category"):
            # Only Main Quiz
            engine = cls()
            should_focus_on_category = True
        else:
            engine = cls
            should_focus_on_category = False
            
        quiz = [(q["question"], q["answer"], q["category"]) for q in quiz]
        results = []
        for quiz_elem, user_answer in zip(quiz, user_answers):
            question, correct_answer, category = quiz_elem
            correct_answer = correct_answer.lower()
            if should_focus_on_category:
                engine.focus_on_category(category)
            user_answer = engine.parse_user_answer(user_answer)
            correct = engine.compare_answers(
                user_answer,
                correct_answer,
            )
            user_answer = engine.prettify_answer(user_answer)
            correct_answer = engine.prettify_answer(correct_answer)
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
