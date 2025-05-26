import unittest
from datetime import datetime, timedelta
from flask import Flask

from app import db
from app.auth_service import AuthService
from app.models import User  # Import from app.models, not core.models


class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["SECRET_KEY"] = "test-secret"

        self.ctx = self.app.app_context()
        self.ctx.push()

        db.init_app(self.app)
        db.create_all()

        self.auth = AuthService(db=db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_register_and_login_success(self):
        success, msg = self.auth.register_user("alice", "securepassword")
        self.assertTrue(success)
        self.assertEqual(msg, "User registered successfully.")

        success, result = self.auth.login_user("alice", "securepassword")
        self.assertTrue(success)
        self.assertIn("user_id", result)

    def test_duplicate_registration(self):
        self.auth.register_user("bob", "pw1")
        success, msg = self.auth.register_user("bob", "pw2")
        self.assertFalse(success)
        self.assertEqual(msg, "Username already exists.")

    def test_login_wrong_password(self):
        self.auth.register_user("carol", "correct")
        success, msg = self.auth.login_user("carol", "wrong")
        self.assertFalse(success)
        self.assertIn("Invalid credentials", msg)

    def test_account_lock_after_failed_attempts(self):
        self.auth.register_user("dave", "topsecret")
        for _ in range(self.auth.max_failed_attempts):
            self.auth.login_user("dave", "badpw")

        success, msg = self.auth.login_user("dave", "topsecret")
        self.assertFalse(success)
        self.assertEqual(msg, "Account is locked. Try again later.")

        user = User.query.filter_by(username="dave").first()
        self.assertIsNotNone(user.lock_until)
        self.assertGreater(user.lock_until, datetime.utcnow())

    def test_verify_password_correctness(self):
        pw = "testpw123"
        hashed = self.auth._hash_password(pw)
        self.assertTrue(self.auth._verify_password(pw, hashed))
        self.assertFalse(self.auth._verify_password("wrongpw", hashed))

    def test_lock_flag_logic(self):
        self.assertFalse(self.auth._is_locked(None))
        future = datetime.utcnow() + timedelta(minutes=5)
        past = datetime.utcnow() - timedelta(minutes=5)
        self.assertTrue(self.auth._is_locked(future))
        self.assertFalse(self.auth._is_locked(past))


if __name__ == "__main__":
    unittest.main()
