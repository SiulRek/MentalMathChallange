from core.date_quiz_engine import DateQuizEngine
from core.math_quiz_engine import MathQuizEngine


class QuizEngine:
    def __init__(self):
        self.active_engine = None

    def _get_engine(self, type):
        if type == "math":
            return MathQuizEngine
        if type == "date":
            return DateQuizEngine
        raise ValueError(
            f"Unsupported quiz type: {type}"
        )

    def generate_quiz(self, blueprint):
        quiz = []
        for sub_blueprint, count in blueprint:
            sub_blueprint["count"] = count
            engine = self._get_engine(sub_blueprint["category"])
            quiz.extend(engine.generate(sub_blueprint))
        return quiz

    def _focus_on_category(self, category):
        self.active_engine = self._get_engine(category)

    def _validate_focused_engine(self):
        if not self.active_engine:
            raise ValueError(
                "No focused engine set. Use focus_on_category() first."
            )

    def _compare_answers(self, answer_a, answer_b):
        self._validate_focused_engine()
        if not answer_a or not answer_b:
            return False
        return self.active_engine.compare_answers(answer_a, answer_b)

    def _parse_user_answer(self, user_answer):
        self._validate_focused_engine()
        try:
            user_answer = user_answer.strip()
        except AttributeError:
            pass
        if not user_answer:
            return None

        return self.active_engine.parse_user_answer(user_answer)

    def _prettify_answer(self, answer):
        self._validate_focused_engine()
        if not answer:
            return None
        return self.active_engine.prettify_answer(answer)

    def compute_quiz_results(self, quiz, user_answers):
        quiz = [(q["question"], q["answer"], q["category"]) for q in quiz]
        results = []
        for quiz_elem, user_answer in zip(quiz, user_answers):
            question, correct_answer, category = quiz_elem
            correct_answer = correct_answer.lower()
            self._focus_on_category(category)
            engine = self.active_engine
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
