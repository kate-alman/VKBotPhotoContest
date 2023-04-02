from typing import Optional

from random import choice

from app.contest.models import (
    MemberModel,
    ContestModel,
    Member,
)
from app.store.contest.accessor import ContestAccessor


class TournamentAccessor:
    def __init__(self, contest_access: ContestAccessor):
        self.contest_access = contest_access

    async def create_members(self, users: list[Member], chat_id: int) -> None:
        await self.contest_access.create_member(users, chat_id)

    async def start_contest(self, chat_id: int, users: list[Member]) -> None:
        """Запускает игру, добавляет участников"""
        await self.contest_access.create_contest(chat_id)
        await self.create_members(users, chat_id)

    async def rerun_contest(self, chat_id: int, users: list[Member]) -> None:
        """Перезапускает уже созданную игру (неактивную)"""
        await self.contest_access.delete_members(chat_id)
        await self.contest_access.rerun_contest(chat_id)
        await self.create_members(users, chat_id)

    async def stop_contest(
        self, chat_id: int, contest: ContestModel, active: Optional[list[Member]] = None
    ) -> MemberModel:
        """Останавливает игру, объявляет победителя"""
        if not active:
            active = self.get_active(contest)
        winner = await self.get_winner(active)
        await self.contest_access.set_inactive_contest(chat_id, winner)
        return winner

    def get_active(self, contest: ContestModel) -> list[MemberModel]:
        """Возвращает список из не выбывших участников"""
        active = [m for m in contest.members if m.active[0].member_active]
        return active

    async def check_points(
        self, pair: tuple[MemberModel, MemberModel], chat_id: int
    ) -> None:
        """Очищает очки перед раундом, если требуется"""
        for member in pair:
            if member.active[0].total:
                await self.contest_access.reset_points(chat_id, member.id)

    async def vote_(self, member_id: int, chat_id: int, vote_id: str) -> None:
        """Голосуем за фотку, проверяем конец раунда"""
        await self.contest_access.add_points(chat_id, vote_id)
        await self.contest_access.set_voted(member_id, chat_id)

    async def start_round(
        self, chat_id: int, contest: ContestModel
    ) -> tuple[MemberModel, MemberModel] | MemberModel:
        """Запускает раунд"""
        active = self.get_active(contest)
        try:
            left, right = await self.next_pair(active)
            await self.check_points((left, right), chat_id)
            await self.contest_access.reset_voted(chat_id)
            return left, right
        except (TypeError, IndexError):
            return await self.stop_contest(chat_id, contest, active)

    async def next_pair(self, active: list[Member]) -> Optional[tuple[Member, Member]]:
        """Выкидывает два рандомных фото, которые еще не участвовали в голосовании"""
        if len(active) == 1:
            return None
        left = choice(active)
        right = choice(active)
        while right == left:
            right = choice(active)
        return left, right

    async def finish_round(
        self,
        chat_id: int,
        contest: ContestModel,
        participants: tuple[MemberModel],
    ) -> None:
        """Завершает раунд, определяет победителя"""
        active = self.get_active(contest)
        await self.round_winner(chat_id, active, participants)

    async def get_winner(self, active: list[MemberModel]) -> MemberModel:
        """Определяет финального победителя"""
        return active[0] if len(active) == 1 else choice(active)

    async def round_winner(
        self,
        chat_id: int,
        active: list[MemberModel],
        participants: tuple[MemberModel],
    ) -> MemberModel:
        """Выбираем победителя и проигравшего в раунде"""
        scores = {i: i.active[0].total for i in active}
        winner = list(
            filter(
                lambda x: x == max(scores, key=scores.get),
                scores,
            )
        )[0]
        loser = participants[0] if participants[1].id == winner.id else participants[1]
        await self.contest_access.drop_member(loser.id, chat_id)
        return loser

    async def get_table(self, contest: ContestModel) -> str:
        """Показывает список не выбывших участников"""
        active = self.get_active(contest)
        return "<br>".join([f"{m.name} {m.surname}" for m in active])

    async def get_statistic(self, contest: ContestModel) -> str:
        winners = "<br>".join(
            [f"У {m.name} {m.surname} {m.winner} побед" for m in contest.members]
        )
        return winners
