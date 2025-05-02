from flask import Flask, render_template, request, session

from src.helpers.fetch_answers import fetch_answers
from src.helpers.generate_questions import generate_questions

app = Flask(__name__)
app.secret_key = "supersecretkey"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    config_text = request.form.get("config", "")

    questions = generate_questions(config_text=config_text)
    session["questions"] = questions
    return render_template("quiz.html", questions=questions)


@app.route("/submit", methods=["POST"])
def submit():
    questions, correct_answers = zip(
        *[(q["question"], q["answer"]) for q in session.get("questions", [])]
    )
    user_answers = fetch_answers(total_expected_answers=len(questions))
    results = []

    for question, correct_answer, user_answer in zip(
        questions, correct_answers, user_answers
    ):
        try:
            user_answer = int(user_answer)
        except ValueError:
            pass
        correct = user_answer == correct_answer
        results.append(
            {
                "question": question,
                "correct_answer": correct_answer,
                "user_answer": user_answer or "Not answered",
                "is_correct": correct,
            }
        )

    return render_template("result.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
