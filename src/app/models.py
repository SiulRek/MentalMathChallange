from app import db
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Boolean

class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(LargeBinary, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    lock_until = Column(DateTime, nullable=True)


class PendingUser(db.Model):
    __tablename__ = "pending_users"

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(LargeBinary, nullable=False)
