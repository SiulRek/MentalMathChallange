from app import db
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime

class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(LargeBinary, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    lock_until = Column(DateTime, nullable=True)
