import json

from sqlalchemy.exc import IntegrityError

from app.models import UserBlueprint
from app.validators import assert_blueprint_name
from quiz import parse_blueprint_from_text
from quiz.units.exceptions import UserConfigError


class BlueprintService:
    def __init__(self, db):
        self.db = db
        self._create_blueprint_table()

    def _create_blueprint_table(self):
        self.db.create_all()

    def add_user_blueprint(self, user_id, name, description, blueprint_text):
        try:
            assert_blueprint_name(name)
        except ValueError as e:
            return False, str(e)

        existing = UserBlueprint.query.filter_by(
            user_id=user_id, name=name
        ).first()
        if existing:
            return False, f"Blueprint '{name}' already exists."

        try:
            blueprint = parse_blueprint_from_text(blueprint_text)
            blueprint = json.dumps(blueprint)
        except UserConfigError as e:
            return False, str(e)

        new_blueprint = UserBlueprint(
            user_id=user_id,
            name=name,
            description=description,
            blueprint=blueprint,
        )
        try:
            self.db.session.add(new_blueprint)
            self.db.session.commit()
            return True, f"Blueprint '{name}' added successfully."
        except IntegrityError:
            self.db.session.rollback()
            return False, "Failed to add blueprint due to integrity error."

    def update_user_blueprint(
        self, user_id, name, description, blueprint_text, new_name=None
    ):
        if new_name:
            try:
                assert_blueprint_name(new_name)
            except ValueError as e:
                return False, str(e)
        blueprint = UserBlueprint.query.filter_by(
            user_id=user_id, name=name
        ).first()
        if not blueprint:
            return False, f"No blueprint named '{name}' found."

        if new_name and new_name != name:
            existing = UserBlueprint.query.filter_by(
                user_id=user_id, name=new_name
            ).first()
            if existing:
                return False, f"Blueprint '{new_name}' already exists."

        try:
            parsed_blueprint = parse_blueprint_from_text(blueprint_text)
            blueprint.blueprint = json.dumps(parsed_blueprint)
        except UserConfigError as e:
            return False, str(e)

        blueprint.description = description
        if new_name:
            blueprint.name = new_name

        self.db.session.commit()
        return True, f"Blueprint '{name}' updated successfully."

    def delete_user_blueprint(self, user_id, name):
        blueprint = UserBlueprint.query.filter_by(
            user_id=user_id, name=name
        ).first()
        if not blueprint:
            return False, f"No blueprint named '{name}' found."

        self.db.session.delete(blueprint)
        self.db.session.commit()
        return True, f"Blueprint '{name}' deleted."

    def get_user_blueprint(self, user_id, name):
        blueprint = UserBlueprint.query.filter_by(
            user_id=user_id, name=name
        ).first()
        if not blueprint:
            return None
        blueprint = {
            "name": blueprint.name,
            "description": blueprint.description,
            "blueprint": json.loads(blueprint.blueprint),
        }
        return blueprint

    def get_user_blueprints_list(self, user_id):
        blueprints = UserBlueprint.query.filter_by(user_id=user_id).all()
        blueprint_list = []
        for blueprint in blueprints:
            blueprint = {
                "name": blueprint.name,
                "description": blueprint.description,
                "blueprint": json.loads(blueprint.blueprint),
            }
            blueprint_list.append(blueprint)
        return blueprint_list
