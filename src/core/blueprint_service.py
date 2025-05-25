import sqlite3


class BlueprintService:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_blueprint_table()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _create_blueprint_table(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_blueprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                blueprint TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """
        )
        conn.commit()
        conn.close()

    def add_user_blueprint(self, user_id, name, blueprint):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM user_blueprints WHERE user_id = ? AND name = ?
        """,
            (user_id, name),
        )
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, f"Blueprint '{name}' already exists."

        cursor.execute(
            """
            INSERT INTO user_blueprints (user_id, name, blueprint) VALUES (?, ?, ?)
        """,
            (user_id, name, blueprint),
        )
        conn.commit()
        conn.close()
        return True, f"Blueprint '{name}' added successfully."

    def delete_user_blueprints(self, user_id, name):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM user_blueprints WHERE user_id = ? AND name = ?
        """,
            (user_id, name),
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        if affected:
            return True, f"Blueprint '{name}' deleted."
        return False, f"No blueprint named '{name}' found."

    def get_user_blueprints_dict(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT name, blueprint FROM user_blueprints WHERE user_id = ?
        """,
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return {name: blueprint for name, blueprint in rows}
