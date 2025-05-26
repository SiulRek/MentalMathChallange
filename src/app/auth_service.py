from datetime import datetime, timedelta
import bcrypt
from sqlalchemy.exc import IntegrityError

from app.models import User  # ✅ db is bound via app.models, no circular import


class AuthService:
    def __init__(self, db, lock_duration=300, max_failed_attempts=3):
        self.db = db
        self.lock_duration = lock_duration
        self.max_failed_attempts = max_failed_attempts
        self._create_user_table()

    def _create_user_table(self):
        self.db.create_all()

    def _assert_username(self, username):
        if not username:
            raise AssertionError("Username cannot be empty.")
        if len(username) < 3:
            raise AssertionError("Username must be at least 3 characters long.")
        if not username.isalnum():
            raise AssertionError("Username must be alphanumeric.")
    
    def _assert_password(self, password):
        if not password:
            raise AssertionError("Password cannot be empty.")
        if len(password) < 6:
            raise AssertionError("Password must be at least 6 characters long.")

    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def _verify_password(self, password, password_hash):
        return bcrypt.checkpw(password.encode("utf-8"), password_hash)

    def _is_locked(self, lock_until):
        return lock_until and datetime.utcnow() < lock_until

    def register_user(self, username, password):
        try:
            self._assert_username(username)
            self._assert_password(password)
        except AssertionError as e:
            return False, str(e)
        
        hashed_pw = self._hash_password(password)
        user = User(username=username, password_hash=hashed_pw)

        try:
            self.db.session.add(user)
            self.db.session.commit()
            return True, "User registered successfully."
        except IntegrityError:
            self.db.session.rollback()
            return False, "Username already exists."

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
            user.lock_until = datetime.utcnow() + timedelta(seconds=self.lock_duration)
            msg = "Too many failed attempts. Account locked."
        else:
            msg = f"Invalid credentials. Attempts: {user.failed_attempts}"

        self.db.session.commit()
        return False, msg
