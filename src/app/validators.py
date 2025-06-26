from app.models import User


def assert_username(username):
    assert username, "Username cannot be empty."
    assert len(username) >= 3, "Username must be at least 3 characters long."
    assert username.isalnum(), "Username must be alphanumeric."
    assert len(username) <= 32, "Username cannot be longer than 32 characters."


def assert_email(email):
    assert email, "Email cannot be empty."
    assert "@" in email and "." in email, "Invalid email format."


def assert_password(password):
    assert password, "Password cannot be empty."
    assert len(password) >= 6, "Password must be at least 6 characters long."
    assert any(char.isdigit() for char in password), \
        "Password must contain at least one digit."
    assert any(char.isalpha() for char in password), \
        "Password must contain at least one letter."
    assert any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in password), \
        "Password must contain at least one special character."
    assert len(password) <= 128, \
        "Password cannot be longer than 128 characters."
    assert any(char.isupper() for char in password), \
        "Password must contain at least one uppercase letter."


def assert_unique_username_and_email(username, email):
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    assert not existing_user, "Username or email already exists in the system."


def assert_blueprint_name(name):
    assert len(name) - len(name.strip()) == 0, \
        "Blueprint name cannot contain leading or trailing spaces."
    assert name, "Blueprint name cannot be empty."
    assert len(name) >= 3, "Blueprint name must be at least 3 characters long."
    assert name.replace(" ", "").isalnum(), \
        "Blueprint name must be alphanumeric, excluding spaces."
    assert len(name) <= 100, \
        "Blueprint name cannot be longer than 100 characters."
