import json

from sqlalchemy.exc import IntegrityError

from app.models import UserBlueprint
from core.parse_blueprint_from_text import (
    parse_blueprint_from_text,
    UserConfigError,
)


class BlueprintService:
    def __init__(self, db):
        self.db = db
        self._create_blueprint_table()

    def _create_blueprint_table(self):
        self.db.create_all()

    def add_user_blueprint(self, user_id, name, description, blueprint_text):
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

    def delete_user_blueprint(self, user_id, name):
        blueprint = UserBlueprint.query.filter_by(
            user_id=user_id, name=name
        ).first()
        if not blueprint:
            return False, f"No blueprint named '{name}' found."

        self.db.session.delete(blueprint)
        self.db.session.commit()
        return True, f"Blueprint '{name}' deleted."


    def get_user_blueprints_list(self, user_id):
        blueprints = UserBlueprint.query.filter_by(user_id=user_id).all()
        blueprint_list = []
        for blueprint in blueprints:
            blueprint = {
                "name": blueprint.name,
                "description": blueprint.description,
                "blueprint": blueprint.blueprint,
            }
            blueprint_list.append(blueprint)
        return blueprint_list
