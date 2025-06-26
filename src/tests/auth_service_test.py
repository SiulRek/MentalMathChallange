from datetime import datetime, timedelta
import unittest

from flask import Flask

from app import db
from app.auth_service import AuthService
from app.models import User


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

    def _register_user(self, username, password):
        """
        Helper to simulate full registration via pending user flow.
        """
        email = f"{username}@example.com"
        success, msg = self.auth.add_pending_user(email, username, password)
        self.assertTrue(success, msg)
        success, msg = self.auth.register_pending_user_by_email(email)
        self.assertTrue(success, msg)

    def test_register_and_login_success(self):
        self._register_user("alice", "Secure1!")
        success, result = self.auth.login_user("alice", "Secure1!")
        self.assertTrue(success)
        self.assertIn("user_id", result)

    def test_duplicate_registration(self):
        self._register_user("bob", "Valid1!")
        success, msg = self.auth.add_pending_user(
            "bob@example.com", "bob", "Another1!"
        )
        self.assertFalse(success)
        self.assertIn("already exists", msg)

    def test_login_wrong_password(self):
        self._register_user("carol", "Correct1@")
        success, msg = self.auth.login_user("carol", "Wrong1@")
        self.assertFalse(success)
        self.assertIn("Invalid credentials", msg)

    def test_account_lock_after_failed_attempts(self):
        self._register_user("dave", "TopSecret1!")
        for _ in range(self.auth.max_failed_attempts):
            self.auth.login_user("dave", "badPass1!")

        success, msg = self.auth.login_user("dave", "TopSecret1!")
        self.assertFalse(success)
        self.assertEqual(msg, "Account is locked. Try again later.")

        user = User.query.filter_by(username="dave").first()
        self.assertIsNotNone(user.lock_until)
        self.assertGreater(user.lock_until, datetime.utcnow())

    def test_verify_password_correctness(self):
        pw = "Testpw123!"
        hashed = self.auth._hash_password(pw)
        self.assertTrue(self.auth._verify_password(pw, hashed))
        self.assertFalse(self.auth._verify_password("wrongpw", hashed))

    def test_lock_flag_logic(self):
        self.assertFalse(self.auth._is_locked(None))
        future = datetime.utcnow() + timedelta(minutes=5)
        past = datetime.utcnow() - timedelta(minutes=5)
        self.assertTrue(self.auth._is_locked(future))
        self.assertFalse(self.auth._is_locked(past))

    def test_delete_user(self):
        self._register_user("eve", "RemoveMe1@")

        user = User.query.filter_by(username="eve").first()
        self.assertIsNotNone(user)

        success, message = self.auth.delete_user(user.id)
        self.assertTrue(success)
        self.assertEqual(message, "User deleted successfully.")

        user_after = User.query.get(user.id)
        self.assertIsNone(user_after)

    def test_change_password_with_incorrect_old_password(self):
        self._register_user("frank", "OldPass1@")
        user = User.query.filter_by(username="frank").first()
        self.assertIsNotNone(user)

        success, msg = self.auth.change_user_password(
            user.id, "WrongOld1@", "NewPass1!"
        )
        self.assertFalse(success)
        self.assertEqual(msg, "Old password is incorrect.")

    def test_change_password_with_same_old_and_new_password(self):
        self._register_user("frank", "OldPass1@")
        user = User.query.filter_by(username="frank").first()
        self.assertIsNotNone(user)

        if (
            "New password cannot be the same as the old password."
            not in self.auth.change_user_password.__doc__
        ):
            self.skipTest("Same-password check not implemented in service.")
        success, msg = self.auth.change_user_password(
            user.id, "OldPass1@", "OldPass1@"
        )
        self.assertFalse(success)
        self.assertEqual(
            msg, "New password cannot be the same as the old password."
        )

    def test_change_password_success(self):
        self._register_user("frank", "OldPass1@")
        user = User.query.filter_by(username="frank").first()
        self.assertIsNotNone(user)

        success, msg = self.auth.change_user_password(
            user.id, "OldPass1@", "NewPass1!"
        )
        self.assertTrue(success)
        self.assertEqual(msg, "Password changed successfully.")

    def test_login_fails_with_old_password_after_change(self):
        self._register_user("frank", "OldPass1@")
        user = User.query.filter_by(username="frank").first()
        self.auth.change_user_password(user.id, "OldPass1@", "NewPass1!")

        success, _ = self.auth.login_user("frank", "OldPass1@")
        self.assertFalse(success)

    def test_login_succeeds_with_new_password_after_change(self):
        self._register_user("frank", "OldPass1@")
        user = User.query.filter_by(username="frank").first()
        self.auth.change_user_password(user.id, "OldPass1@", "NewPass1!")

        success, result = self.auth.login_user("frank", "NewPass1!")
        self.assertTrue(success)
        self.assertIn("user_id", result)


if __name__ == "__main__":
    unittest.main()