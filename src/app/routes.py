from datetime import datetime
from functools import wraps
import json

from flask import render_template, request, session, redirect, url_for, flash

from app.email_utils import send_confirmation_email, decode_email_token
from core.compute_quiz_results import compute_quiz_results, UserResponseError
from core.generate_quiz import generate_quiz
from core.unparse_blueprint_to_text import unparse_blueprint_to_text


def _login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "info")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def _register_authentication_and_user_management_routes(app):
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]

            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return render_template("register.html")

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
        pending_email = session["pending_email"]

        confirmed = app.auth.is_user_email_confirmed(pending_email)
        if confirmed:
            session.pop("pending_email")
            return redirect(url_for("login"))

        message = "A confirmation email has been sent. "
        message += "Please check your inbox and confirm."
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
                message="Email confirmed successfully!",
                type="email_confirmation_success",
            )
        return render_template(
            "message.html", message=message, type="email_confirmation_error"
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if "user_id" in session:
            return redirect(url_for("index"))

        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            success, result = app.auth.login_user(username, password)
            if success:
                session["user_id"] = result["user_id"]
                session["username"] = username
                return redirect(url_for("index"))
            flash(result, "error")

        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    @_login_required
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.route("/user-settings")
    @_login_required
    def user_settings():
        return render_template("user_settings.html")

    @app.route("/delete-account", methods=["GET", "POST"])
    @_login_required
    def delete_account():
        if request.method == "POST":
            if request.form.get("confirm") == "yes":
                app.auth.delete_user(session["user_id"])
                session.clear()
                flash("Your account has been deleted.", "info")
                return redirect(url_for("login"))
            flash("Account deletion cancelled.", "info")
            return redirect(url_for("user_settings"))
        return render_template("confirm_delete.html")

    @app.route("/change-password", methods=["GET", "POST"])
    @_login_required
    def change_password():
        if request.method == "POST":
            old_password = request.form["old_password"]
            new_password = request.form["new_password"]
            confirm_password = request.form["confirm_password"]

            if new_password != confirm_password:
                flash("New passwords do not match.", "error")
                return render_template("change_password.html")

            success, msg = app.auth.change_user_password(
                session["user_id"], old_password, new_password
            )
            if success:
                flash("Password changed successfully.", "success")
                return redirect(url_for("user_settings"))
            else:
                flash(msg, "error")

        return render_template("change_password.html")



def _register_blueprint_management_routes(app):
    @app.route("/", methods=["GET", "POST"])
    def index():
        if "user_id" not in session:
            return redirect(url_for("login"))

        user_id = session["user_id"]

        if request.method == "POST":
            blueprint_name = request.form["blueprint_name"]
            action = request.form["action"]

            if action == "delete":
                success, message = app.bp_service.delete_user_blueprint(
                    user_id, blueprint_name
                )
                if not success:
                    flash(message, "error")
                return redirect(url_for("index"))

            elif action == "quiz":
                blueprint_entry = app.bp_service.get_user_blueprint(
                    user_id, blueprint_name
                )
                session["blueprint"] = blueprint_entry["blueprint"]
                return redirect(url_for("quiz"))

            else:
                raise ValueError(f"Unknown action: {action}")

        session.clear()
        session["user_id"] = user_id

        blueprints = app.bp_service.get_user_blueprints_list(user_id)
        blueprints.sort(key=lambda x: x["name"].lower())
        return render_template("index.html", blueprints=blueprints)

    @app.route("/create_blueprint", methods=["GET", "POST"])
    @_login_required
    def create_blueprint():
        if request.method == "POST":
            name = request.form["name"]
            description = request.form["description"].strip()
            blueprint_text = request.form["blueprint"]

            if not name or not blueprint_text:
                flash("Name and blueprint text cannot be empty.", "error")
                return render_template(
                    "create_blueprint.html",
                    name=name,
                    description=description,
                    blueprint=blueprint_text,
                )

            success, message = app.bp_service.add_user_blueprint(
                user_id=session["user_id"],
                name=name,
                description=description,
                blueprint_text=blueprint_text,
            )
            if success:
                return redirect(url_for("index"))
            flash(message, "error")

        return render_template(
            "create_blueprint.html", name="", description="", blueprint=""
        )

    @app.route("/edit_blueprint", methods=["GET", "POST"])
    @_login_required
    def edit_blueprint():
        user_id = session["user_id"]

        if request.method == "POST":
            original_name = request.form["original_name"]
            new_name = request.form["name"]
            description = request.form["description"].strip()
            blueprint_text = request.form["blueprint"]

            if not new_name or not blueprint_text:
                flash("Name and blueprint text cannot be empty.", "error")
                return render_template(
                    "edit_blueprint.html",
                    name=new_name,
                    description=description,
                    blueprint=blueprint_text,
                    original_name=original_name,
                )

            success, message = app.bp_service.update_user_blueprint(
                user_id=user_id,
                name=original_name,
                new_name=new_name,
                description=description,
                blueprint_text=blueprint_text,
            )
            if success:
                flash(
                    f"Blueprint '{new_name}' updated successfully.", "success"
                )
                return redirect(url_for("index"))
            flash(message, "error")

        name = request.args["name"]
        blueprint_entry = app.bp_service.get_user_blueprint(
            user_id=user_id, name=name
        )
        if not blueprint_entry:
            raise ValueError(f"No blueprint found with name '{name}'.")

        blueprint = unparse_blueprint_to_text(blueprint_entry["blueprint"])
        return render_template(
            "edit_blueprint.html",
            name=blueprint_entry["name"],
            description=blueprint_entry["description"],
            blueprint=blueprint,
            original_name=blueprint_entry["name"],
        )


def _register_quiz_routes(app):
    @app.route("/quiz", methods=["GET", "POST"])
    @_login_required
    def quiz():
        if request.form.get("retry_incorrect") and request.method == "POST":
            results = session["results"]
            session["quiz"] = create_quiz_from_incorrect_results(results)
            session["start_time"] = datetime.utcnow().isoformat()
            return render_template("quiz.html", quiz=session["quiz"])

        blueprint = json.loads(session["blueprint"])
        quiz = generate_quiz(blueprint)
        session["quiz"] = quiz
        session["start_time"] = datetime.utcnow().isoformat()
        return render_template("quiz.html", quiz=quiz)

    def create_quiz_from_incorrect_results(results):
            incorrect_results = [
                res for res in results if not res["is_correct"]
            ]
            return [
                {
                    "question": res["question"],
                    "answer": res["correct_answer"],
                    "category": res["category"],
                }
                for res in incorrect_results
            ]

    @app.route("/submit", methods=["POST"])
    @_login_required
    def submit():
        quiz = session["quiz"]
        try:
            results = compute_quiz_results(quiz, submission=request.form)
        except UserResponseError as e:
            previous_answers = {
                k: v
                for k, v in request.form.items()
                if k.startswith("answer_")
            }
            return render_template(
                "quiz.html",
                quiz=quiz,
                error=str(e),
                previous_answers=previous_answers,
            )

        session["results"] = results
        return redirect(url_for("result"))

    @app.route("/result", methods=["GET", "POST"])
    @_login_required
    def result():
        results = session["results"]
        duration = calculate_duration()
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

    def calculate_duration():
        start_time = datetime.fromisoformat(session["start_time"])
        stop_time = (
            datetime.fromisoformat(session.get("stop_time"))
            if session.get("stop_time")
            else datetime.utcnow()
        )
        if stop_time < start_time:
            stop_time = datetime.utcnow()
        session["stop_time"] = stop_time.isoformat()
        return (stop_time - start_time).total_seconds()


def _register_miscellaneous_routes(app):
    @app.route("/help")
    def help_page():
        return render_template("help.html")


def register_routes(app):
    _register_authentication_and_user_management_routes(app)
    _register_blueprint_management_routes(app)
    _register_quiz_routes(app)
    _register_miscellaneous_routes(app)

    @app.route("/health")
    def health_check():
        return "OK", 200