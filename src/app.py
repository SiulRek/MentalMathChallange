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
    return render_template("quiz.html", quiz=quiz)

@app.route("/submit", methods=["POST"])
def submit():
    quiz = session.get("quiz", [])
    try:
        results = compute_quiz_results(quiz, submission=request.form)
    except UserResponseError as e:
        return render_template("quiz.html", quiz=quiz, error=str(e))
    return render_template("result.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
