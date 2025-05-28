import os

from flask import current_app
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app import mail

if os.getenv("RUNNING_LOCALLY", "false") == "true":
    INDEX_URL = "http://localhost:5000/"
else:
    INDEX_URL = "https://mentalmathchallange-1.onrender.com/"


def send_confirmation_email(user_email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = serializer.dumps(user_email, salt="email-confirm")
    link = f"{INDEX_URL}confirm/{token}"

    msg = Message(
        subject="Confirm your Email",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[user_email],
    )
    msg.body = f"Click the link to confirm your email: {link}"
    mail.send(msg)


def decode_email_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token, salt="email-confirm", max_age=expiration
        )
        return email
    except (BadSignature, SignatureExpired):
        return None