from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import joinedload

from app.contest.models import (
    ContestModel,
    MemberModel,
    MembersContestsModel,
    Member,
    Contest,
)
from app.store import Database


class ContestAccessor:
    def __init__(self, db: Database):
        self.database = db

    async def rerun_contest(self, chat_id: int) -> None:
        async with self.database.session.begin() as session:
            """Перезапускает контест"""
            query = (
                update(ContestModel)
                .where(ContestModel.id == chat_id)
                .values(is_active=True)
            )
            await session.execute(query)

    async def get_contest_by_id(self, chat_id: int) -> Optional[ContestModel]:
        """Находит контест в бд по id и возвращает всю информацию по нему, если такого нет, возвращает None"""
        async with self.database.session.begin() as session:
            query = (
                select(ContestModel)
                .options(
                    joinedload(ContestModel.members).joinedload(
                        MemberModel.active.and_(
                            MembersContestsModel.contest_id == chat_id
                        )
                    )
                )
                .filter(ContestModel.id == chat_id)
            )
            contest = (await session.execute(query)).scalar()
            if contest:
                return contest
        return None

    async def create_contest(self, chat_id: int) -> ContestModel:
        """Добавляет контест в бд"""
        async with self.database.session.begin() as session:
            contest = ContestModel(is_active=True, id=chat_id)
            session.add(contest)
            return contest

    async def set_inactive_contest(self, chat_id: int, winner: MemberModel) -> None:
        """Меняет статус контеста и его участников в бд на неактивный.
        Статус участников меняется для корректной обработки досрочной обработки игры"""
        async with self.database.session.begin() as session:
            query = (
                update(ContestModel)
                .where(ContestModel.id == chat_id)
                .values(
                    is_active=False,
                    winner=f"{winner.name} {winner.surname}" if winner else None,
                )
            )
            await session.execute(query)

            query = (
                update(MembersContestsModel)
                .where(MembersContestsModel.contest_id == chat_id)
                .values(member_active=False)
            )
            await session.execute(query)
            if winner:
                query = (
                    update(MemberModel)
                    .where(MemberModel.id == winner.id)
                    .values(winner=MemberModel.winner + 1)
                )
                await session.execute(query)

    async def add_points(self, chat_id: int, member_id: str) -> None:
        """Начисляет очки раунда"""
        async with self.database.session.begin() as session:
            query = (
                update(MembersContestsModel)
                .where(MembersContestsModel.member_id == member_id)
                .where(MembersContestsModel.contest_id == chat_id)
                .values(total=MembersContestsModel.total + 1)
            )
            await session.execute(query)

    async def reset_points(self, chat_id: int, member_id: int) -> None:
        """Сбрасывает очки перед раундом"""
        async with self.database.session.begin() as session:
            query = (
                update(MembersContestsModel)
                .where(MembersContestsModel.member_id == member_id)
                .where(MembersContestsModel.contest_id == chat_id)
                .values(total=0)
            )
            await session.execute(query)

    async def create_member(self, users: list[Member], chat_id: int) -> None:
        """Добавляет участника в бд"""
        async with self.database.session.begin() as session:
            in_query = insert(MemberModel).values(
                [
                    {
                        "id": user.id,
                        "name": user.name,
                        "surname": user.surname,
                        "photo": user.photo,
                    }
                    for user in users
                ]
            )
            query_r = in_query.on_conflict_do_update(
                index_elements=[MemberModel.id],
                set_=dict(photo=in_query.excluded.photo),
            )
            await session.execute(query_r)
            query = insert(MembersContestsModel).values(
                [{"member_id": user.id, "contest_id": chat_id} for user in users]
            )

            query = query.on_conflict_do_update(
                index_elements=[
                    MembersContestsModel.member_id,
                    MembersContestsModel.contest_id,
                ],
                set_=dict(member_active=True, total=0),
                index_where=(MembersContestsModel.contest_id == chat_id),
            )

            await session.execute(query)

    async def set_voted(self, member_id: int, chat_id: int) -> None:
        """Меняет выбывшему участнику статус, чтобы он не мог до конца игры еще раз участвовать"""
        async with self.database.session.begin() as session:
            query = (
                update(MembersContestsModel)
                .where(MembersContestsModel.contest_id == chat_id)
                .where(MembersContestsModel.member_id == member_id)
                .values(voted=True)
            )
            await session.execute(query)

    async def reset_voted(self, chat_id: int) -> None:
        """Меняет выбывшему участнику статус, чтобы он не мог до конца игры еще раз участвовать"""
        async with self.database.session.begin() as session:
            query = (
                update(MembersContestsModel)
                .where(MembersContestsModel.contest_id == chat_id)
                .values(voted=False)
            )
            await session.execute(query)

    async def drop_member(self, member_id: int, chat_id: int) -> None:
        """Меняет выбывшему участнику статус, чтобы он не мог до конца игры еще раз участвовать"""
        async with self.database.session.begin() as session:
            query = (
                update(MembersContestsModel)
                .where(MembersContestsModel.contest_id == chat_id)
                .where(MembersContestsModel.member_id == member_id)
                .values(member_active=False)
            )
            await session.execute(query)

    async def delete_members(self, chat_id: int) -> None:
        """Удаляет данные об игре из manytomany"""
        async with self.database.session.begin() as session:
            query = delete(MembersContestsModel).where(
                MembersContestsModel.contest_id == chat_id
            )
            await session.execute(query)

    async def get_contests(
        self, is_active: Optional[bool] = None
    ) -> Optional[list[Contest]]:
        """Выводит список контестов"""
        async with self.database.session.begin() as session:
            query = (
                select(ContestModel)
                if not is_active
                else select(ContestModel).where(ContestModel.is_active)
            )
            answ = (await session.execute(query)).scalars().unique()
            contests = [contest.to_dc() for contest in answ]
            if contests:
                return contests
        return None
