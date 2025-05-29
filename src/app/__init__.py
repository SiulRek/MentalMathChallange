import os

from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()


def configure_app(app):
    app.config["SECRET_KEY"] = "dev-secret"

    default_db = "sqlite:///app_database.db"
    url = os.getenv("DATABASE_URL", default_db)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = url

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "luiskraker2000@gmail.com"
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(__file__), "../templates"
        ),
        static_folder=os.path.join(os.path.dirname(__file__), "../static"),
    )
    configure_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    mail.init_app(app)

    with app.app_context():
        from app.auth_service import AuthService

        app.auth = AuthService(db=db)

        from app.routes import register_routes

        register_routes(app)

    return app
