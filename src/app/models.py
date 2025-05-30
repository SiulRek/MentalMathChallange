import sqlite3

from sqlalchemy import (
    Column,
    Integer,
    String,
    LargeBinary,
    DateTime,
    ForeignKey,
    Text,
    event,
    UniqueConstraint,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship, backref

from app import db


# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(LargeBinary, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    lock_until = Column(DateTime, nullable=True)

    blueprints = relationship(
        "UserBlueprint",
        backref=backref("user", passive_deletes=True),
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class PendingUser(db.Model):
    __tablename__ = "pending_users"

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(LargeBinary, nullable=False)


class UserBlueprint(db.Model):
    __tablename__ = "user_blueprints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    blueprint = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="_user_blueprint_uc"),
    )
