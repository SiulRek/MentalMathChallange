from core.date_quiz_generator import DateQuizGenerator
from core.math_quiz_generator import MathQuizGenerator
from core.quiz_generator_base import QuizGeneratorBase


class QuizGenerator(QuizGeneratorBase):
    def __init__(self):
        self.focused_gen = None

    def _get_generator(self, generator_type):
        """
        Get the appropriate quiz generator class.

        Parameters
        ----------
        generator_type : str
            The type of quiz generator ('math' or 'date').

        Returns
        -------
        Type
            The corresponding quiz generator class.

        Raises
        ------
        ValueError
            If the quiz type is unsupported.
        """
        if generator_type == "math":
            return MathQuizGenerator
        if generator_type == "date":
            return DateQuizGenerator
        raise ValueError(
            f"Unsupported quiz type: {generator_type}"
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
            quiz_gen = self._get_generator(sub_blueprint["category"])
            quiz.extend(quiz_gen.generate(sub_blueprint))
        return quiz

    def focus_on_category(self, category):
        self.focused_gen = self._get_generator(category)

    def _validate_focused_generator(self):
        if not self.focused_gen:
            raise ValueError(
                "No focused generator set. Use focus_on_category() first."
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
            True if the answers match according to the generator's logic, False
            otherwise.
        """
        self._validate_focused_generator()
        if not answer_a or not answer_b:
            return False
        return self.focused_gen.compare_answers(answer_a, answer_b)

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
        self._validate_focused_generator()
        try:
            user_answer = user_answer.strip()
        except AttributeError:
            pass
        if not user_answer:
            return None

        return self.focused_gen.parse_user_answer(user_answer)

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
        self._validate_focused_generator()
        if not answer:
            return None
        return self.focused_gen.prettify_answer(answer)


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
    quiz_gen = QuizGenerator()
    return quiz_gen.generate(blueprint)
