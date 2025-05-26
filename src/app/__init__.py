import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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
        "DATABASE_URL", "sqlite:///app.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        from app.models import User
        from app.auth_service import AuthService

        app.auth = AuthService(db=db)

        from app.routes import register_routes

        register_routes(app)

    return app
