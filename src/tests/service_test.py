from datetime import datetime, timedelta
import os
import unittest

from core.auth_service import AuthService
from core.blueprint_service import BlueprintService
from tests.utils.base_test_case import BaseTestCase


class TestAuthService(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.db_path = os.path.join(self.temp_dir, "auth_test.db")
        self.auth = AuthService(db_path=self.db_path)

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

    def test_is_locked_edge_case(self):
        self.assertFalse(self.auth._is_locked(None))
        self.assertFalse(self.auth._is_locked("invalid-date"))
        future = (datetime.now() + timedelta(minutes=5)).isoformat()
        past = (datetime.now() - timedelta(minutes=5)).isoformat()
        self.assertTrue(self.auth._is_locked(future))
        self.assertFalse(self.auth._is_locked(past))

    def test_verify_password_correctness(self):
        pw = "testpw123"
        hashed = self.auth._hash_password(pw)
        self.assertTrue(self.auth._verify_password(pw, hashed))
        self.assertFalse(self.auth._verify_password("wrongpw", hashed))


class TestBlueprintService(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.db_path = os.path.join(self.temp_dir, "blueprint_test.db")
        self.auth = AuthService(db_path=self.db_path)
        self.bp = BlueprintService(db_path=self.db_path)
        self.auth.register_user("erin", "pw")
        self.user_id = self.auth.login_user("erin", "pw")[1]["user_id"]

    def test_add_and_get_blueprint(self):
        success, msg = self.bp.add_user_blueprint(
            self.user_id, "api", "json-v1"
        )
        self.assertTrue(success)
        self.assertIn("added successfully", msg)
        result = self.bp.get_user_blueprints_dict(self.user_id)
        self.assertEqual(result, {"api": "json-v1"})

    def test_add_duplicate_blueprint(self):
        self.bp.add_user_blueprint(self.user_id, "main", "config-A")
        success, msg = self.bp.add_user_blueprint(
            self.user_id, "main", "config-B"
        )
        self.assertFalse(success)
        self.assertIn("already exists", msg)

    def test_delete_existing_and_nonexisting_blueprint(self):
        self.bp.add_user_blueprint(self.user_id, "dev", "blueprint1")
        success, msg = self.bp.delete_user_blueprints(self.user_id, "dev")
        self.assertTrue(success)
        self.assertIn("deleted", msg)
        success, msg = self.bp.delete_user_blueprints(self.user_id, "dev")
        self.assertFalse(success)
        self.assertIn("No blueprint", msg)


class TestIntegration(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.db_path = os.path.join(self.temp_dir, "integration_test.db")
        self.auth = AuthService(db_path=self.db_path)
        self.bp = BlueprintService(db_path=self.db_path)

    def test_register_login_add_and_fetch_blueprint(self):
        self.auth.register_user("max", "pw")
        user_id = self.auth.login_user("max", "pw")[1]["user_id"]
        self.bp.add_user_blueprint(user_id, "daily", "schedule")
        blueprints = self.bp.get_user_blueprints_dict(user_id)
        self.assertEqual(blueprints, {"daily": "schedule"})


if __name__ == "__main__":
    unittest.main()
