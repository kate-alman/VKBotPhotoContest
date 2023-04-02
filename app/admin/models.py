from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from sqlalchemy import Integer, String, Column

from app.store.database.sqlalchemy_base import db


@dataclass
class Admin:
    email: str
    id: Optional[int] = None
    password: Optional[str] = None

    def is_password_valid(self, password: str) -> bool:
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["Admin"]:
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])


class AdminModel(db):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)

    def to_dc(self) -> Admin:
        return Admin(id=self.id, email=self.email, password=self.password)
