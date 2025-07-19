from quiz.units.date_quiz_unit import DateQuizUnit
from quiz.units.math_quiz_unit import MathQuizUnit
from quiz.units.memory_quiz_unit import MemoryQuizUnit

QUIZ_UNIT_MAPPING = {
    "date": DateQuizUnit,
    "math": MathQuizUnit,
    "memory": MemoryQuizUnit,
    # TODO: Add more quiz units as needed
}
