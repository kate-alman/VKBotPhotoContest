from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db


@dataclass
class Member:
    id: int
    name: str
    surname: str
    photo: str
    winner: Optional[int] = None


@dataclass
class Contest:
    id: int
    is_active: bool
    winner: str


@dataclass
class MembersContests:
    member_id: int
    contest_id: int
    member_active: bool
    total: int


class MemberModel(db):
    __tablename__ = "members"
    id = Column(Integer(), primary_key=True)
    name = Column(String(), nullable=False, default="Name")
    surname = Column(String(), nullable=False, default="Surname")
    photo = Column(String(), nullable=False, default=0)
    winner = Column(Integer(), nullable=False, default=0)
    contests = relationship("ContestModel", secondary="members_contests", viewonly=True)
    active = relationship("MembersContestsModel", backref="members")

    def to_dc(self) -> Member:
        return Member(
            id=self.id,
            name=self.name,
            surname=self.surname,
            photo=self.photo,
            winner=self.winner,
        )


class ContestModel(db):
    __tablename__ = "contests"
    id = Column(Integer(), primary_key=True)
    is_active = Column(Boolean(), nullable=False, default=False)
    winner = Column(String(), nullable=True)
    members = relationship("MemberModel", secondary="members_contests", viewonly=True)

    def to_dc(self) -> Contest:
        return Contest(id=self.id, is_active=self.is_active, winner=self.winner)


class MembersContestsModel(db):
    __tablename__ = "members_contests"

    contest_id = Column(
        ForeignKey("contests.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
    member_id = Column(
        ForeignKey("members.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
    voted = Column(Integer(), default=False)
    member_active = Column(Boolean(), nullable=False, default=True)
    total = Column(Integer(), default=0)

    def to_dc(self) -> MembersContests:
        return MembersContests(
            contest_id=self.contest_id,
            member_id=self.member_id,
            member_active=self.member_active,
            total=self.total,
        )
