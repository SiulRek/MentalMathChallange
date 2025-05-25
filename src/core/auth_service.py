from datetime import datetime, timedelta
import sqlite3
import bcrypt


class AuthService:
    def __init__(self, db_path, lock_duration=300, max_failed_attempts=3):
        self.db_path = db_path
        self.lock_duration = lock_duration
        self.max_failed_attempts = max_failed_attempts
        self._create_user_table()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _create_user_table(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                lock_until TEXT DEFAULT NULL
            )
        """
        )
        conn.commit()
        conn.close()

    @staticmethod
    def _hash_password(password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    @staticmethod
    def _verify_password(password, password_hash):
        return bcrypt.checkpw(password.encode("utf-8"), password_hash)

    @staticmethod
    def _is_locked(lock_until):
        if lock_until:
            try:
                return datetime.now() < datetime.fromisoformat(lock_until)
            except ValueError:
                return False
        return False

    def register_user(self, username, password):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, self._hash_password(password)),
            )
            conn.commit()
            return True, "User registered successfully."
        except sqlite3.IntegrityError:
            return False, "Username already exists."
        finally:
            conn.close()

    def login_user(self, username, password):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, password_hash, failed_attempts, lock_until FROM users WHERE username = ?
        """,
            (username,),
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Invalid username or password."

        user_id, password_hash, failed_attempts, lock_until = row

        if self._is_locked(lock_until):
            conn.close()
            return False, "Account is locked. Try again later."

        if self._verify_password(password, password_hash):
            cursor.execute(
                """
                UPDATE users SET failed_attempts = 0, lock_until = NULL WHERE id = ?
            """,
                (user_id,),
            )
            conn.commit()
            conn.close()
            return True, {"user_id": user_id}

        failed_attempts += 1
        if failed_attempts >= self.max_failed_attempts:
            lock_time = (
                datetime.now() + timedelta(seconds=self.lock_duration)
            ).isoformat()
            cursor.execute(
                """
                UPDATE users SET failed_attempts = ?, lock_until = ? WHERE id = ?
            """,
                (failed_attempts, lock_time, user_id),
            )
            msg = "Too many failed attempts. Account locked."
        else:
            cursor.execute(
                """
                UPDATE users SET failed_attempts = ? WHERE id = ?
            """,
                (failed_attempts, user_id),
            )
            msg = f"Invalid credentials. Attempts: {failed_attempts}"

        conn.commit()
        conn.close()
        return False, msg
