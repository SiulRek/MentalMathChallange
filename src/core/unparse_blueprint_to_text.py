import json
from core.quiz_engine import QuizEngine

def unparse_blueprint_to_text(blueprint):
    """
    Converts parsed blueprint data back to the original raw blueprint text
    format.

    Parameters
    ----------
    blueprint_data : list of tuple(dict, int) or str
        List of tuples where each tuple contains an expression blueprint
        dictionary and a count, or a JSON string representing such a list.

    Returns
    -------
    str
        Reconstructed blueprint as a human-readable string.
    """
    return QuizEngine().unparse_blueprint_to_text(blueprint)
