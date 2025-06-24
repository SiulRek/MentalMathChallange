import json
import unittest

from flask import Flask

from app import db
from app.auth_service import AuthService
from app.blueprint_service import BlueprintService
from app.models import User, UserBlueprint
from core.parse_blueprint_from_text import parse_blueprint_from_text


class TestBlueprintService(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["SECRET_KEY"] = "test-secret"

        db.init_app(self.app)
        self.app.app_context().push()
        db.app = self.app
        db.create_all()

        self.auth = AuthService(db=db)
        self.bp_service = BlueprintService(db=db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _register_user(self, username, password):
        email = f"{username}@example.com"
        success, msg = self.auth.add_pending_user(email, username, password)
        self.assertTrue(success, msg)
        success, msg = self.auth.register_pending_user_by_email(email)
        self.assertTrue(success, msg)
        return User.query.filter_by(username=username).first()

    def test_add_blueprint_success(self):
        user = self._register_user("alice", "Strong1!")
        blueprint_text = "math: 1\n int 1 10\n op +\n const pi"
        success, msg = self.bp_service.add_user_blueprint(
            user.id, "bp1", "desc", blueprint_text
        )
        self.assertTrue(success)
        self.assertIn("added successfully", msg)

        stored = UserBlueprint.query.filter_by(
            user_id=user.id, name="bp1"
        ).first()
        self.assertIsNotNone(stored)
        expected = json.dumps(parse_blueprint_from_text(blueprint_text))
        self.assertEqual(stored.blueprint, expected)

    def test_add_duplicate_blueprint(self):
        user = self._register_user("bob", "Strong1!")
        blueprint_text = "math: 1\n int 1 10\n"
        self.bp_service.add_user_blueprint(
            user.id, "bp1", "desc1", blueprint_text
        )
        success, msg = self.bp_service.add_user_blueprint(
            user.id, "bp1", "desc2", blueprint_text
        )
        self.assertFalse(success)
        self.assertIn("already exists", msg)

    def test_get_user_blueprints_list(self):
        user = self._register_user("carol", "Strong1!")
        bp1 = "math: 1\n int 1 10\n"
        bp2 = "math: 1\n int 2 20\n"
        self.bp_service.add_user_blueprint(user.id, "bp_one", "desc1", bp1)
        self.bp_service.add_user_blueprint(user.id, "bp_two", "desc2", bp2)

        bp_list = self.bp_service.get_user_blueprints_list(user.id)
        names = [bp["name"] for bp in bp_list]
        self.assertEqual(len(bp_list), 2)
        self.assertIn("bp_one", names)
        self.assertIn("bp_two", names)

    def test_update_existing_blueprint(self):
        user = self._register_user("dave", "Strong1!")
        blueprint_text = "math: 1\n int 1 10\n"
        self.bp_service.add_user_blueprint(
            user.id, "bp_to_update", "desc", blueprint_text
        )

        new_blueprint_text = "math: 2\n int 2 20\n"
        success, msg = self.bp_service.update_user_blueprint(
            user.id, "bp_to_update", "new desc", new_blueprint_text
        )
        self.assertTrue(success)
        self.assertIn("updated successfully", msg)

        updated_bp = UserBlueprint.query.filter_by(
            user_id=user.id, name="bp_to_update"
        ).first()
        expected = json.dumps(parse_blueprint_from_text(new_blueprint_text))
        self.assertEqual(updated_bp.blueprint, expected)

    
    def test_update_existing_blueprint_with_new_name(self):
        user = self._register_user("dave", "Strong1!")
        blueprint_text = "math: 1\n int 1 10\n"
        self.bp_service.add_user_blueprint(
            user.id, "bp_to_update", "desc", blueprint_text
        )

        new_blueprint_text = "math: 2\n int 2 20\n"
        success, msg = self.bp_service.update_user_blueprint(
            user.id,
            "bp_to_update",
            "new desc",
            new_blueprint_text,
            "new_bp_name",
        )
        self.assertTrue(success)
        self.assertIn("updated successfully", msg)

        updated_bp = UserBlueprint.query.filter_by(
            user_id=user.id, name="new_bp_name"
        ).first()
        expected = json.dumps(parse_blueprint_from_text(new_blueprint_text))
        self.assertEqual(updated_bp.blueprint, expected)

    def test_delete_existing_blueprint(self):
        user = self._register_user("dave", "Strong1!")
        blueprint_text = "math: 1\n int 1 10\n"
        self.bp_service.add_user_blueprint(
            user.id, "to_delete", "desc", blueprint_text
        )
        success, msg = self.bp_service.delete_user_blueprint(
            user.id, "to_delete"
        )
        self.assertTrue(success)
        self.assertIn("deleted", msg)

        bp = UserBlueprint.query.filter_by(
            user_id=user.id, name="to_delete"
        ).first()
        self.assertIsNone(bp)

    def test_delete_nonexistent_blueprint(self):
        user = self._register_user("eve", "Strong1!")
        success, msg = self.bp_service.delete_user_blueprint(user.id, "ghost")
        self.assertFalse(success)
        self.assertIn("No blueprint named", msg)

    def test_delete_user_blueprints(self):
        user = self._register_user("frank", "Strong1!")
        bp1 = "math: 1\n int 1 10\n"
        bp2 = "math: 1\n int 2 20\n"
        self.bp_service.add_user_blueprint(user.id, "bp1", "desc1", bp1)
        self.bp_service.add_user_blueprint(user.id, "bp2", "desc2", bp2)

        success, msg = self.auth.delete_user(user.id)
        self.assertTrue(success)
        self.assertIn("deleted successfully", msg)

        remaining = UserBlueprint.query.filter_by(user_id=user.id).all()
        self.assertEqual(len(remaining), 0)

    def test_cross_user_blueprint_isolated(self):
        user1 = self._register_user("user1", "Strong1!")
        user2 = self._register_user("user2", "Strong1!")

        bp1 = "math: 1\n int 1 10\n"
        bp2 = "math: 1\n int 1 10\n"

        self.bp_service.add_user_blueprint(user1.id, "bp", "user1 bp", bp1)
        self.bp_service.add_user_blueprint(user2.id, "bp", "user2 bp", bp2)

        bps1 = self.bp_service.get_user_blueprints_list(user1.id)
        bps2 = self.bp_service.get_user_blueprints_list(user2.id)

        self.assertEqual(len(bps1), 1)
        self.assertEqual(len(bps2), 1)
        self.assertEqual(bps1[0]["blueprint"], bps2[0]["blueprint"])


if __name__ == "__main__":
    unittest.main()
