from datetime import datetime
from functools import wraps

from flask import render_template, request, session, redirect, url_for, flash

from app.email_utils import send_confirmation_email, decode_email_token
from core.compute_quiz_results import compute_quiz_results, UserResponseError
from core.generate_quiz import generate_quiz
from core.parse_blueprint_from_text import (
    parse_blueprint_from_text,
    UserConfigError,
)


def register_routes(app):
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
            email = request.form.get("email", "")
            password = request.form.get("password", "")

            success, message = app.auth.add_pending_user(
                email, username, password
            )
            if success:
                send_confirmation_email(email)
                session["pending_email"] = email
                return redirect(url_for("request_email_confirmation"))
            flash(message, "error")
        return render_template("register.html")

    @app.route("/request-email-confirmation")
    def request_email_confirmation():
        pending_email = session.get("pending_email", None)
        if not pending_email:
            flash(
                "No email with pending confirmation found in this session.",
                "error",
            )
            return redirect(url_for("register"))
        confirmed = app.auth.is_user_email_confirmed(pending_email)
        if confirmed:
            return redirect(url_for("login"))
        message = (
            "A confirmation email has been sent to your email address. "
            "Please check your inbox and click the link to confirm your email."
        )
        return render_template(
            "message.html", message=message, type="request_email_confirmation"
        )

    @app.route("/confirm/<token>")
    def confirm_email(token):
        email = decode_email_token(token)
        if not email:
            return render_template(
                "message.html",
                message="Invalid or expired confirmation link.",
                type="email_confirmation_error",
            )

        success, message = app.auth.register_pending_user_by_email(email)
        if not success:
            success = app.auth.is_user_email_confirmed(email)
        if success:
            return render_template(
                "message.html",
                message="Email confirmed successfully! You can now log in.",
                type="email_confirmation_success",
            )
        else:
            return render_template(
                "message.html",
                message=message,
                type="email_confirmation_error",
            )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if "user_id" in session:
            return redirect(url_for("index"))

        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            success, result = app.auth.login_user(username, password)
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
