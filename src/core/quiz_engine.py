from core.date_quiz_unit import DateQuizUnit
from core.exceptions import UserConfigError
from core.math_quiz_unit import MathQuizUnit


class QuizEngine:
    def __init__(self):
        self.active_engine = None

    def _parse_options(self, text):
        options = []
        lines = text.strip().splitlines()
        for line in lines:
            args = line.strip().split()
            key = args[0]
            args = args[1:] if len(args) > 1 else []
            options.append({"key": key, "args": args})
        return options

    def _get_engine(self, type):
        if type == "math":
            return MathQuizUnit
        if type == "date":
            return DateQuizUnit
        raise ValueError(
            f"Unsupported quiz type: {type}"
        )

    def parse_blueprint_from_text(self, text):
        blueprint = []
        lines = text.splitlines()
        i = 0

        while i < len(lines):
            line = lines[i].rstrip()
            if not line.lstrip():
                i += 1
                continue
            if line.startswith(" "):
                raise UserConfigError(
                    f"Unexpected indentation in blueprint block: '{line}'"
                )

            # Parse the block header
            if ":" not in line:
                raise UserConfigError(
                    f"Invalid blueprint block start: '{line}'"
                )

            try:
                category, count = line.split(":")
                category = category.strip()
                quiz_unit = self._get_engine(category)
                count = int(count.strip())
            except ValueError as exc:
                raise UserConfigError(
                    f"Invalid blueprint block start: '{line}'"
                ) from exc

            i += 1

            # Parse the block body
            block_text = ""
            while i < len(lines) and (
                lines[i].startswith(" ") or not lines[i]
            ):
                if not lines[i].strip():
                    i += 1
                    continue
                block_text += lines[i].rstrip() + "\n"
                i += 1
            options = self._parse_options(block_text)
            blueprint_unit = quiz_unit.generate_blueprint_unit(options)

            blueprint_unit.update({"category": category})
            blueprint.append((blueprint_unit, count))

        return blueprint

    def generate_quiz(self, blueprint):
        quiz = []
        for unit_blueprint, count in blueprint:
            category = unit_blueprint.get("category")
            unit_blueprint["count"] = count
            engine = self._get_engine(category)
            quiz.extend(engine.generate_quiz(unit_blueprint))
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
