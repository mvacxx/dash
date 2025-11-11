import hashlib
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String

from .base import Base


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = _hash_password(password)

    def verify_password(self, password: str) -> bool:
        return self.password_hash == _hash_password(password)
