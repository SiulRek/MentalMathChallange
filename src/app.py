from flask import Flask, render_template, request, session

from src.core.compute_quiz_results import compute_quiz_results
from src.core.generate_quiz import generate_quiz

app = Flask(__name__)
app.secret_key = "supersecretkey"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    config_text = request.form.get("config", "")
    quiz = generate_quiz(config_text=config_text)
    session["quiz"] = quiz
    return render_template("quiz.html", quiz=quiz)


@app.route("/submit", methods=["POST"])
def submit():
    quiz = session.get("quiz", [])
    results = compute_quiz_results(
        quiz, submission=request.form
    )
    return render_template("result.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
