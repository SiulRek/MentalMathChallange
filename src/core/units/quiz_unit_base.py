from abc import ABC, abstractmethod


class QuizUnitBase(ABC):
    """
    Base class for quiz engines unit that handle specific types of quizzes.
    """

    @classmethod
    @abstractmethod
    def generate_blueprint_unit(cls, options):
        """
        Convert options to a blueprint unit for the quiz engine.
        """
        pass
    
    @classmethod
    @abstractmethod
    def unparse_options(cls, blueprint_unit):
        """
        Convert a blueprint unit back to options for the quiz engine.
        """
        pass
    
    @classmethod
    @abstractmethod
    def generate_quiz(cls, blueprint_unit):
        """
        Generate a quiz based on the provided blueprint_unit.
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
