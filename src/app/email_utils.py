import os
import random

from flask import current_app
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app import mail

if os.getenv("RUNNING_LOCALLY", "false") == "true":
    INDEX_URL = "http://localhost:5000/"
else:
    INDEX_URL = "https://mentalmathchallange-1.onrender.com/"


def generate_salt(seed):
    random.seed(seed)
    return "".join(
        random.choices(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            k=32,
        )
    )


TYPE_SALT_MAPPING = {
    "email-confirm": generate_salt(seed="email-confirm"),
    "password-reset": generate_salt(seed="password-reset"),
}

random.seed()  # Reset seed to system default


def send_confirmation_email(user_email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    salt = TYPE_SALT_MAPPING["email-confirm"]
    token = serializer.dumps(user_email, salt=salt)
    link = f"{INDEX_URL}confirm/{token}"

    msg = Message(
        subject="Confirm your Email",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[user_email],
    )
    msg.body = f"Click the link to confirm your email: {link}"
    mail.send(msg)


def decode_email_token(token, expiration=300, type="email-confirm"):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    salt = TYPE_SALT_MAPPING[type]
    try:
        email = serializer.loads(
            token, salt=salt, max_age=expiration
        )
        return email
    except (BadSignature, SignatureExpired):
        return None


def send_password_reset_email(user_email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    salt = TYPE_SALT_MAPPING["password-reset"]
    token = serializer.dumps(user_email, salt=salt)
    link = f"{INDEX_URL}reset-password/{token}"

    msg = Message(
        subject="Password Reset Request",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[user_email],
    )
    msg.body = f"Click the link to reset your password: {link}"
    mail.send(msg)
