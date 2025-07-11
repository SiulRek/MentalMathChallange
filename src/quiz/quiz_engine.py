from quiz.units import QUIZ_UNIT_MAPPING
from quiz.units.exceptions import UserConfigError


class QuizEngine:
    def __init__(self):
        self._active_unit = None

    def _parse_options(self, text):
        options = []
        lines = text.strip().splitlines()
        for line in lines:
            args = line.strip().split()
            args = [arg for arg in args if arg]
            key = args[0]
            args = args[1:] if len(args) > 1 else []
            options.append({"key": key, "args": args})
        return options

    def _get_quiz_unit(self, type):
        quiz_unit = QUIZ_UNIT_MAPPING.get(type, None)
        if quiz_unit:
            return quiz_unit
        raise KeyError(
            f"Unsupported quiz type: '{type}'"
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
                quiz_unit = self._get_quiz_unit(category)
                count = int(count.strip())
            except ValueError as exc:
                raise UserConfigError(
                    f"Invalid blueprint block start: '{line}'"
                ) from exc
            except KeyError as exc:
                raise UserConfigError(str(exc)) from exc

            if count < 1:
                raise UserConfigError(
                    f"Invalid count in blueprint block: '{line}'"
                )

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
            blueprint_unit = quiz_unit.transform_options_to_blueprint_unit(
                options
            )

            blueprint_unit.update({"count": count})
            blueprint.append((blueprint_unit, category))

        return blueprint

    def unparse_blueprint_to_text(self, blueprint):
        text = ""
        for blueprint_unit, category in blueprint:
            text += f"{category}: {blueprint_unit.pop('count')}\n"
            quiz_unit = self._get_quiz_unit(category)
            options = quiz_unit.transform_blueprint_unit_to_options(blueprint_unit)
            text += "\n".join(
                f"  {opt['key']} {' '.join(opt['args'])}" for opt in options
            )
            text += "\n\n"
        return text.strip()

    def generate_quiz(self, blueprint):
        quiz = []
        for blueprint_unit, category in blueprint:
            q_unit = self._get_quiz_unit(category)
            quiz.extend(q_unit.generate_quiz(blueprint_unit))
        return quiz

    def _focus_on_category(self, category):
        self._active_unit = self._get_quiz_unit(category)

    def _compare_answers(self, answer_a, answer_b):
        if not answer_a or not answer_b:
            return False
        return self._active_unit.compare_answers(answer_a, answer_b)

    def _parse_user_answer(self, user_answer):
        try:
            user_answer = user_answer.strip()
        except AttributeError:
            pass
        if not user_answer:
            return None

        return self._active_unit.parse_user_answer(user_answer)

    def _prettify_answer(self, answer):
        return self._active_unit.prettify_answer(answer)

    def compute_quiz_results(self, quiz, user_answers):
        quiz = [(q["question"], q["answer"], q["category"]) for q in quiz]
        results = []
        for quiz_elem, user_answer in zip(quiz, user_answers):
            question, correct_answer, category = quiz_elem
            self._focus_on_category(category)
            user_answer = self._parse_user_answer(user_answer)
            correct = self._compare_answers(
                user_answer,
                correct_answer,
            )
            user_answer = self._prettify_answer(user_answer)
            correct_answer = self._prettify_answer(correct_answer)
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
