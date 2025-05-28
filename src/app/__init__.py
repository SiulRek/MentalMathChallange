import os

from flask import Flask

from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

mail = Mail()

db = SQLAlchemy()


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(__file__), "../templates"
        ),
        static_folder=os.path.join(os.path.dirname(__file__), "../static"),
    )

    app.config["SECRET_KEY"] = "dev-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///app_database.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "luiskraker2000@gmail.com"
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from app.models import User
        from app.auth_service import AuthService

        app.auth = AuthService(db=db)

        from app.routes import register_routes

        register_routes(app)

    return app
