from abc import ABC, abstractmethod


class QuizGeneratorBase(ABC):
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
    def compare_answer(cls, answer_a, answer_b):
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
