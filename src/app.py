import random

from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = "supersecretkey"


def generate_questions(n=10):
    operations = ["+", "-", "*"]
    questions = []
    for _ in range(n):
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        op = random.choice(operations)
        expr = f"{a} {op} {b}"
        result = eval(expr)
        questions.append({"question": expr, "answer": result})
    return questions


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    questions = generate_questions()
    session["questions"] = questions
    return render_template("quiz.html", questions=questions)


def _retrieve_answers(sorted_answers, length):
    def _get_index(item):
        try:
            key = item[0]
        except (ValueError, IndexError):
            raise ValueError(
                f"Invalid answer key '{item[0]}'. Expected format "
                "'answer_<index>'."
            )
        return int(key.split("_")[1])

    for i in range(length - 1):
        try:
            key = f"answer_{i}"
            if key not in sorted_answers:
                sorted_answers[key] = None
        except (ValueError, IndexError):
            pass
    sorted_answers = dict(sorted(sorted_answers.items(), key=_get_index))
    sorted_answers = list(sorted_answers.values())
    return sorted_answers


@app.route("/submit", methods=["POST"])
def submit():
    questions, correct_answers = zip(
        *[(q["question"], q["answer"]) for q in session.get("questions", [])]
    )
    user_answers = _retrieve_answers(request.form, length=len(questions))
    results = []

    for question, correct_answer, user_answer in zip(
        questions, correct_answers, user_answers
    ):
        try:
            user_result = int(user_answer)
        except (ValueError, TypeError):
            raise ValueError(
                f"Invalid answer '{user_answer}' for question '{question}'."
            )
        correct = user_result == correct_answer
        results.append(
            {
                "question": question,
                "correct_answer": correct_answer,
                "user_answer": user_result,
                "is_correct": correct,
            }
        )

    return render_template("result.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
