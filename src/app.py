from datetime import datetime

from flask import Flask, render_template, request, session

from src.core.compute_quiz_results import (
    compute_quiz_results,
    UserResponseError,
)
from src.core.generate_quiz import generate_quiz
from src.core.parse_blueprint_from_text import (
    parse_blueprint_from_text,
    UserConfigError,
)

app = Flask(__name__)
app.secret_key = "supersecretkey"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/help")
def help_page():
    return render_template("help.html")


@app.route("/start", methods=["POST"])
def start():
    blueprint_text = request.form.get("blueprint", "")
    try:
        blueprint = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(blueprint)
    except UserConfigError as e:
        return render_template(
            "index.html", blueprint_text=blueprint_text, error=str(e)
        )

    session["quiz"] = quiz
    session["start_time"] = datetime.utcnow().isoformat()  # Store start time
    return render_template("quiz.html", quiz=quiz)


@app.route("/submit", methods=["POST"])
def submit():
    quiz = session.get("quiz", [])
    start_time_str = session.get("start_time")

    try:
        results = compute_quiz_results(quiz, submission=request.form)
    except UserResponseError as e:
        return render_template("quiz.html", quiz=quiz, error=str(e))

    duration = None
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str)
        duration = datetime.utcnow() - start_time

    total = len(results)
    correct = sum(1 for r in results if r["is_correct"])
    incorrect = total - correct
    percentage = round((correct / total) * 100) if total > 0 else 0

    return render_template(
        "result.html",
        results=results,
        duration=duration,
        correct=correct,
        incorrect=incorrect,
        percentage=percentage
    )



if __name__ == "__main__":
    app.run(debug=True)
