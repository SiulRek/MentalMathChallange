from core.date_quiz_engine import DateQuizEngine
from core.math_quiz_engine import MathQuizEngine
from core.quiz_engine_base import QuizEngineBase


class MainQuizEngine(QuizEngineBase):
    def __init__(self):
        self.active_engine = None

    def _get_engine(self, type):
        """
        Get the appropriate quiz engine class.

        Parameters
        ----------
        engine_type : str
            The type of quiz engine ('math' or 'date').

        Returns
        -------
        Type
            The corresponding quiz engine class.

        Raises
        ------
        ValueError
            If the quiz type is unsupported.
        """
        if type == "math":
            return MathQuizEngine
        if type == "date":
            return DateQuizEngine
        raise ValueError(
            f"Unsupported quiz type: {type}"
        )

    def generate(self, blueprint):
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
        quiz = []
        for sub_blueprint, count in blueprint:
            sub_blueprint["count"] = count
            engine = self._get_engine(sub_blueprint["category"])
            quiz.extend(engine.generate(sub_blueprint))
        return quiz

    def focus_on_category(self, category):
        self.active_engine = self._get_engine(category)

    def _validate_focused_engine(self):
        if not self.active_engine:
            raise ValueError(
                "No focused engine set. Use focus_on_category() first."
            )

    def compare_answers(self, answer_a, answer_b):
        """
        Compare two answers for a given category.

        Parameters
        ----------
        answer_a : any
            The first answer to compare.
        answer_b : any
            The second answer to compare.

        Returns
        -------
        bool
            True if the answers match according to the engine's logic, False
            otherwise.
        """
        self._validate_focused_engine()
        if not answer_a or not answer_b:
            return False
        return self.active_engine.compare_answers(answer_a, answer_b)

    def parse_user_answer(self, user_answer):
        """
        Parse a user's raw answer for a given category.

        Parameters
        ----------
        user_answer : str
            The raw answer input from the user.

        Returns
        -------
        any or None
            The parsed answer or None if the input is invalid.
        """
        self._validate_focused_engine()
        try:
            user_answer = user_answer.strip()
        except AttributeError:
            pass
        if not user_answer:
            return None

        return self.active_engine.parse_user_answer(user_answer)

    def prettify_answer(self, answer):
        """
        Return a human-readable version of an answer.

        Parameters
        ----------
        answer : any
            The answer to prettify.

        Returns
        -------
        str or None
            The prettified answer or None if the answer is invalid.
        """
        self._validate_focused_engine()
        if not answer:
            return None
        return self.active_engine.prettify_answer(answer)


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
    return engine.generate(blueprint)
