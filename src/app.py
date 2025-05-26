from datetime import datetime
from functools import wraps
import os

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
)

from core.auth_service import AuthService
from core.compute_quiz_results import compute_quiz_results, UserResponseError
from core.generate_quiz import generate_quiz
from core.parse_blueprint_from_text import (
    parse_blueprint_from_text,
    UserConfigError,
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "users.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

auth = AuthService(db_path=DB_PATH)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "info")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/help")
def help_page():
    return render_template("help.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        success, message = auth.register_user(username, password)
        if success:
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
        flash(message, "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        success, result = auth.login_user(username, password)
        if success:
            session["user_id"] = result["user_id"]
            session["username"] = username
            return redirect(url_for("index"))
        flash(result, "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/start", methods=["POST"])
@login_required
def start():
    blueprint_text = request.form.get("blueprint", "")
    try:
        blueprint = parse_blueprint_from_text(blueprint_text)
        quiz = generate_quiz(blueprint)
    except UserConfigError as e:
        return render_template(
            "index.html", blueprint_text=blueprint_text, error=str(e)
        )

    user_id = session["user_id"]
    session[f"quiz_{user_id}"] = quiz
    session["start_time"] = datetime.utcnow().isoformat()
    return render_template("quiz.html", quiz=quiz)


@app.route("/submit", methods=["POST"])
@login_required
def submit():
    user_id = session["user_id"]
    quiz = session.get(f"quiz_{user_id}", [])
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
        percentage=percentage,
    )


if __name__ == "__main__":
    app.run(debug=True)