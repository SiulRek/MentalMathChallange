from datetime import datetime, timedelta

import bcrypt
from sqlalchemy.exc import IntegrityError

from app.models import User, PendingUser
from app.validators import (
    assert_username,
    assert_email,
    assert_password,
    assert_unique_username_and_email,
)


class AuthService:
    def __init__(self, db, lock_duration=300, max_failed_attempts=3):
        self.db = db
        self.lock_duration = lock_duration
        self.max_failed_attempts = max_failed_attempts
        self._create_user_table()

    def _create_user_table(self):
        self.db.create_all()

    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def _verify_password(self, password, password_hash):
        return bcrypt.checkpw(password.encode("utf-8"), password_hash)

    def _is_locked(self, lock_until):
        return lock_until and datetime.utcnow() < lock_until

    def add_pending_user(self, email, username, password):
        try:
            assert_username(username)
            assert_email(email)
            assert_password(password)
            assert_unique_username_and_email(username, email)
        except AssertionError as e:
            return False, str(e)

        hashed_pw = self._hash_password(password)
        pending_user = PendingUser(
            email=email, username=username, password_hash=hashed_pw
        )

        try:
            self.db.session.add(pending_user)
            self.db.session.commit()
            return True, "Pending user added successfully."
        except IntegrityError as e:
            self.db.session.rollback()
            existing_user = PendingUser.query.filter(
                (PendingUser.email == email)
                | (PendingUser.username == username)
            ).first()
            if existing_user:
                existing_user.email = email
                existing_user.username = username
                existing_user.password_hash = hashed_pw
                self.db.session.commit()
                return True, "Pending user added successfully."
            return False, f"Could not add pending user, because of {e}."

    def register_pending_user_by_email(self, email):
        pending_user = PendingUser.query.filter_by(email=email).first()
        if not pending_user:
            return False, "No pending user found with this email."

        user = User(
            username=pending_user.username,
            email=pending_user.email,
            password_hash=pending_user.password_hash,
        )

        try:
            self.db.session.add(user)
            self.db.session.delete(pending_user)
            self.db.session.commit()
            return True, "User registered successfully."
        except IntegrityError:
            self.db.session.rollback()
            return False, "Username or email already exists."

    def is_user_email_confirmed(self, email):
        user = User.query.filter_by(email=email).first()
        return bool(user)

    def login_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        if not user:
            return False, "Invalid username or password."

        if self._is_locked(user.lock_until):
            return False, "Account is locked. Try again later."

        if self._verify_password(password, user.password_hash):
            user.failed_attempts = 0
            user.lock_until = None
            self.db.session.commit()
            return True, {"user_id": user.id}

        user.failed_attempts += 1
        if user.failed_attempts >= self.max_failed_attempts:
            user.failed_attempts = 0
            user.lock_until = datetime.utcnow() + timedelta(
                seconds=self.lock_duration
            )
            msg = "Too many failed attempts. Account locked."
        else:
            msg = f"Invalid credentials. Attempts: {user.failed_attempts}"

        self.db.session.commit()
        return False, msg

    def delete_user(self, user_id):
        print(f"Attempting to delete user with ID: {user_id}")
        user = User.query.get(user_id)
        if not user:
            return False, "User not found."

        self.db.session.delete(user)
        self.db.session.commit()
        return True, "User deleted successfully."
    
    def change_user_password(self, user_id, old_password, new_password):
        user = User.query.get(user_id)
        if not user:
            return False, "User not found."

        if not self._verify_password(old_password, user.password_hash):
            return False, "Old password is incorrect."

        if old_password == new_password:
            return False, "New password cannot be the same as the old password."
        
        try:
            assert_password(new_password)
        except AssertionError as e:
            return False, str(e)

        user.password_hash = self._hash_password(new_password)
        self.db.session.commit()
        return True, "Password changed successfully."
    
    def reset_user_password_by_email(self, email, new_password):
        user = User.query.filter_by(email=email).first()
        if not user:
            return False, "User not found."

        try:
            assert_password(new_password)
        except AssertionError as e:
            return False, str(e)

        user.password_hash = self._hash_password(new_password)
        self.db.session.commit()
        return True, "Password updated successfully."

    def is_existing_user_email(self, email):
        return User.query.filter_by(email=email).first() is not None
