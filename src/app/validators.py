from app.models import User


def assert_username(username):
    if not username:
        raise AssertionError(
            "Username cannot be empty."
        )
    if len(username) < 3:
        raise AssertionError(
            "Username must be at least 3 characters long."
        )
    if not username.isalnum():
        raise AssertionError(
            "Username must be alphanumeric."
        )
    if len(username) > 32:
        raise AssertionError(
            "Username cannot be longer than 32 characters."
        )


def assert_email(email):
    if not email:
        raise AssertionError(
            "Email cannot be empty."
        )
    if "@" not in email or "." not in email:
        raise AssertionError(
            "Invalid email format."
        )


def assert_password(password):
    if not password:
        raise AssertionError(
            "Password cannot be empty."
        )
    if len(password) < 6:
        raise AssertionError(
            "Password must be at least 6 characters long."
        )
    if not any(char.isdigit() for char in password):
        raise AssertionError(
            "Password must contain at least one digit."
        )
    if not any(char.isalpha() for char in password):
        raise AssertionError(
            "Password must contain at least one letter."
        )
    if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in password):
        raise AssertionError(
            "Password must contain at least one special character."
        )
    if len(password) > 128:
        raise AssertionError("Password cannot be longer than 128 characters.")


def assert_unique_username_and_email(username, email):
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        raise AssertionError("Username or email already exists in the system.")
