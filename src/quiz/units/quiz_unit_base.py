from abc import ABC, abstractmethod


class QuizUnitBase(ABC):
    """
    Abstract base class for quiz units that handle specific types of quizzes.

    Subclasses should implement all class methods to provide behavior specific
    to the quiz type (e.g., date-based, math-based). These methods control how
    quiz data is generated, transformed, and evaluated.

    This interface is designed to be compatible with the `QuizEngine` system.
    """

    @classmethod
    @abstractmethod
    def transform_options_to_blueprint_unit(cls, options):
        """
        Convert a list of user-defined options into a structured blueprint
        unit.

        Parameters
        ----------
        options : list of dict
            A list of option dictionaries, where each dictionary contains:
            - 'key' : str
            - 'args' : list of str

        Returns
        -------
        dict
            A blueprint unit representing the parsed configuration for quiz
            generation. This dictionary must contain all necessary data for
            generating questions and answers.

        Raises
        ------
        UserConfigError
            If required options are missing or invalid.
        """
        pass

    @classmethod
    @abstractmethod
    def transform_blueprint_unit_to_options(cls, blueprint_unit):
        """
        Convert a blueprint unit back into a list of option dictionaries.

        Parameters
        ----------
        blueprint_unit : dict
            The structured quiz configuration, produced by
            `transform_options_to_blueprint_unit`.

        Returns
        -------
        list of dict
            A list of options, where each option is a dict with:
            - 'key' : str
            - 'args' : list of str
        """
        pass

    @classmethod
    @abstractmethod
    def generate_quiz(cls, blueprint_unit):
        """
        Generate quiz questions and answers from a blueprint unit.

        Parameters
        ----------
        blueprint_unit : dict
            A dictionary that includes all required configuration parameters
            and a 'count' field indicating how many quiz items to generate.

        Returns
        -------
        list of dict
            A list of quiz elements. Each element is a dict with:
            - 'question' : str
            - 'answer' : Any
            - 'category' : str
        """
        pass

    @classmethod
    @abstractmethod
    def parse_user_answer(cls, user_answer):
        """
        Convert the user's raw input into a standardized internal format.

        Parameters
        ----------
        user_answer : str
            Raw answer text provided by the user.

        Returns
        -------
        str or None
            The normalized answer.

        Raises
        ------
        UserResponseError
            If the input is invalid or cannot be parsed.
        """
        pass

    @classmethod
    @abstractmethod
    def compare_answers(cls, user_answer, correct_answer):
        """
        Compare a user-provided answer with the correct answer.

        Parameters
        ----------
        user_answer : str or None
            The parsed user answer.
        correct_answer : str or None
            The correct answer for comparison.

        Returns
        -------
        bool
            True if the answers match or are equivalent; otherwise False.
        """
        pass

    @classmethod
    @abstractmethod
    def prettify_answer(cls, answer):
        """
        Format an answer into a human-readable form for display.

        Parameters
        ----------
        answer : str
            The answer to format.

        Returns
        -------
        str
            A string representation of the answer, suitable for display.
        """
        pass
