import asyncio
import logging
import re
from dataclasses import asdict
from typing import Optional

import typing

import bson
from aio_pika import IncomingMessage
from aiohttp.web_exceptions import HTTPForbidden
from aiormq import ChannelInvalidStateError

from app.contest.models import MemberModel, Member, ContestModel
from app.app_services.pika_queue import RabbitMQ
from app.store import Database
from app.store.contest.accessor import ContestAccessor

from info import Info
from info import Const
from app.store.tournament.accessor import TournamentAccessor
from app.app_services.vk_api import VkApiAccessor

from app.app_services.vk_api import Message, Update
from app.app_services.vk_api import (
    START_CONTEST_KEYBOARD,
    COMMAND_START_KEYBOARD,
    CONTEST_KEYBOARD,
    set_inline_keyboard,
)


class BotWorker:
    def __init__(self, cfg):
        self.config = cfg
        self.commands: dict[str, typing.Callable] = dict()
        self.rabbitMQ = RabbitMQ(
            host=cfg.rabbitmq.host,
            port=cfg.rabbitmq.port,
            user=cfg.rabbitmq.user,
            password=cfg.rabbitmq.password,
        )
        self._tasks = []
        self.workers = 10
        self.routing_key_worker = "worker"
        self.routing_key_sender = "sender"
        self.routing_key_poller = "poller"
        self.queue_name = "vk_bot"
        self.database = Database(cfg=cfg)
        self.contest_acc = ContestAccessor(self.database)
        self.vk_api = VkApiAccessor(config=cfg)
        self.tournament = TournamentAccessor(self.contest_acc)
        self.timer = False
        self.logger = logging.getLogger("worker")
        self.is_running = False

    async def start(self) -> None:
        self.set_commands()
        await self.vk_api.connect()
        await self.database.connect()
        await self.rabbitMQ.connect()
        self._tasks = [
            asyncio.create_task(self._worker_rabbit()) for _ in range(self.workers)
        ]
        self.is_running = True

    async def stop(self) -> None:
        self.timer = False
        self.is_running = False
        for task in self._tasks:
            task.cancel()
        await self.vk_api.disconnect()
        await self.rabbitMQ.disconnect()
        await self.database.disconnect()

    async def _worker_rabbit(self) -> None:
        """
        Метод для прослушивания событий RabbitMQ.
        """
        await self.rabbitMQ.listen_events(
            on_message_func=self.on_message,
            routing_key=[self.routing_key_worker, self.routing_key_poller],
            queue_name=self.queue_name,
        )

    @staticmethod
    def get_command(text: str) -> tuple:
        """Если нажата кнопка, выдает команду, если сообщение, то проверяется, команда ли это"""
        if "button" in text:
            command = re.findall(r'[^{"buton:}]\w*', text)[0]
            # При голосовании кнопки это id участников
            return ("vote", int(command)) if command.isdigit() else (command, None)
        command = text.strip().lower().split()[0]
        return command, None

    async def on_message(self, message: IncomingMessage) -> None:
        if message.routing_key == "poller":
            update = Update.from_dict(bson.loads(message.body))
            await self._handler(update)
        elif message.routing_key == self.routing_key_worker:
            pass
        await message.ack()

    @staticmethod
    def _check_private_convarsation(id_: int) -> bool:
        """ID групповых чатов начинаются с 2000000000"""
        return id_ < Const.GROUP_CHAT

    @staticmethod
    def check_user_amount(users: list[Member]) -> bool:
        return True if len(users) > 2 else False

    @staticmethod
    def check_user_voted(user_id: int, contest: ContestModel) -> bool:
        try:
            flag = [m.active[0].voted for m in contest.members if m.id == user_id][0]
        except IndexError:
            flag = False
        return flag

    def set_commands(self) -> None:
        self.commands = {
            "start": self._activate_bot,
            "starting": self._begin_contest,
            "vote": self._vote,
            "help": self._help,
            "rules": self._rules,
            "score": self._get_score,
            "stop": self._stop,
            "history": self._history,
            "statistic": self._statistic,
        }

    def _check_invite_bot(self, id_: int | str) -> bool:
        """Сранивает id приглашенного с id группы,
        умножение на -1, потому что при эвентах, вк передает айдишники групп отрицательными,
        не беру проверяемый айди по модулю, потому что это может быть строкой,
        чтобы доп. ошибки не ловить"""
        return self.config.bot.group_id * -1 == id_

    async def _handler(self, update: Update) -> None:
        """Колдует сообщение из обновления и передает обработчику"""
        try:
            if self._check_invite_bot(update.object.body):
                # Если бота добавили в беседу, просит права админа
                message = Message(
                    receiver_id=update.object.peer_id,
                    text=Info.PERMISSION_REQUEST,
                    keyboard=COMMAND_START_KEYBOARD,
                )
            else:
                contest = await self.contest_acc.get_contest_by_id(
                    update.object.peer_id
                )
                command, participant = self.get_command(update.object.body)
                message = await self.commands[command](
                    update=update, vote_id=participant, contest=contest
                )
        except (IndexError, KeyError):
            return
        except HTTPForbidden as e:
            message = Message(
                receiver_id=update.object.peer_id,
                text=e.reason,
                keyboard=COMMAND_START_KEYBOARD,
            )
        if message:
            await self.rabbitMQ.send_event(
                message=asdict(message), routing_key=self.routing_key_sender
            )

    async def _activate_bot(
        self,
        update: Update,
        vote_id: Optional[str] = None,
        contest: Optional[ContestModel] = None,
    ) -> Message:
        chat_id = update.object.peer_id
        if self._check_private_convarsation(chat_id):
            # если бота запустили в личных сообщениях, то отправит предупреждение
            return Message(
                receiver_id=chat_id,
                text=Info.PRIVATE_CONVERSATION,
                keyboard=COMMAND_START_KEYBOARD,
            )
        # если админа нет, выкинет исключение и напишет об этом
        await self.vk_api.get_conversation_members(chat_id)
        # отправляет приглашение к началу игры и стартовую клавиатуру вместо кнопки start
        return Message(
            receiver_id=chat_id,
            text=Info.INVITE_TO_START,
            keyboard=START_CONTEST_KEYBOARD,
        )

    async def _begin_contest(
        self,
        update: Update,
        vote_id: Optional[str] = None,
        contest: Optional[ContestModel] = None,
    ) -> Optional[Message]:
        keyboard = CONTEST_KEYBOARD
        chat_id = update.object.peer_id
        users = await self.vk_api.get_conversation_members(chat_id)
        # проверяет, что пользователей в беседе достаточно для начала игры
        if not self.check_user_amount(users):
            return Message(
                receiver_id=chat_id,
                text=Info.BAD_USER_AMOUNT,
                keyboard=COMMAND_START_KEYBOARD,
            )
        else:
            if contest is None:
                await self.tournament.start_contest(chat_id, users)
                contest = await self.contest_acc.get_contest_by_id(chat_id)

            elif contest.is_active and not self.timer:
                # если игра уже запущена, отправляет предупреждающее сообщение
                message = Message(
                    receiver_id=chat_id,
                    text=Info.GAME_RERUN,
                    keyboard=keyboard,
                )
                await self.rabbitMQ.send_event(
                    message=asdict(message), routing_key=self.routing_key_sender
                )
            elif contest.is_active and self.timer:
                # если игра уже запущена, отправляет предупреждающее сообщение
                message = Message(
                    receiver_id=chat_id,
                    text=Info.GAME_ALREADY_RUNNING,
                    keyboard=keyboard,
                )
                return await self.rabbitMQ.send_event(
                    message=asdict(message), routing_key=self.routing_key_sender
                )
            else:
                await self.tournament.rerun_contest(chat_id, users)
                contest = await self.contest_acc.get_contest_by_id(chat_id)
                # стартовое сообщение с обновлением клавиатуры
            message = Message(
                receiver_id=chat_id, text=Info.START_MESSAGE, keyboard=CONTEST_KEYBOARD
            )
            await self.rabbitMQ.send_event(
                message=asdict(message), routing_key=self.routing_key_sender
            )
            # стартует раунд
            return await self._next_round(update=update, contest=contest)

    async def _check_time_out(
        self, update: Update, participants: tuple[MemberModel]
    ) -> None:
        self.timer = True
        await asyncio.sleep(Const.ROUND_TIME)
        chat_id = update.object.peer_id
        try:
            if self.is_running:
                contest = await self.contest_acc.get_contest_by_id(chat_id=chat_id)
                await self.tournament.finish_round(chat_id, contest, participants)
                current_game = await self.contest_acc.get_contest_by_id(chat_id=chat_id)
                self.timer = False
                message = await self._next_round(update=update, contest=current_game)
                await self.rabbitMQ.send_event(
                    message=asdict(message), routing_key=self.routing_key_sender
                )
        except IndexError:
            pass
        except ChannelInvalidStateError as e:
            self.logger.info(f"{Info.SOMETHING_BROKE} {e}")
        finally:
            return None

    async def _next_round(
        self,
        update: Update,
        contest: Optional[ContestModel] = None,
    ) -> Message:
        """Вытаскивает из моделек фотки и подгружает в инлайн кнопки айдишники участников"""
        chat_id = update.object.peer_id
        round_participant = await self.tournament.start_round(chat_id, contest)
        if isinstance(round_participant, tuple):
            message_attach = ",".join(
                [f"photo{participant.photo}" for participant in round_participant]
            )
            keyboard = set_inline_keyboard(
                *[participant for participant in round_participant]
            )

            # запускает таймер раунда
            asyncio.create_task(
                self._check_time_out(update=update, participants=round_participant)
            )
        else:
            return await self._win_user(update=update, winner=round_participant)

        return Message(
            receiver_id=chat_id,
            attachment=message_attach,
            keyboard=keyboard,
        )

    async def _vote(
        self, update: Update, vote_id: str, contest: Optional[ContestModel] = None
    ) -> Optional[Message]:
        if not self.check_user_voted(update.object.user_id, contest):
            await self.tournament.vote_(
                update.object.user_id, update.object.peer_id, vote_id
            )
        else:
            user = list(
                filter(lambda u: u.id == update.object.user_id, contest.members)
            )
            message = (
                Info.STOP_GAME
                if not user
                else f"@id{update.object.user_id}({user[0].name} {user[0].surname})! {Info.ALREADY_VOTED}"
            )
            return Message(
                receiver_id=update.object.peer_id,
                text=message,
                keyboard=CONTEST_KEYBOARD,
            )

    async def _stop(
        self,
        update: Update,
        vote_id: Optional[str] = None,
        contest: Optional[ContestModel] = None,
    ) -> Message:
        """Останавливает игру и объявляет победителя"""
        chat_id = update.object.peer_id
        if not contest.is_active:
            return Message(
                receiver_id=chat_id,
                text=f"{Info.GAME_ALREADY_STOP} {contest.winner}",
                keyboard=START_CONTEST_KEYBOARD,
            )
        winner = await self.tournament.stop_contest(chat_id, contest)
        if winner:
            return await self._win_user(update, winner)
        else:
            return Message(
                receiver_id=chat_id,
                text=Info.STOP_GAME,
                keyboard=START_CONTEST_KEYBOARD,
            )

    async def _win_user(
        self,
        update: Update,
        winner: Member,
        vote_id: Optional[str] = None,
        contest: Optional[ContestModel] = None,
    ) -> Message:
        """Возвращает победителя"""
        message_text = (
            f"{Info.ANNOUNCE_WINNER} {winner.name} {winner.surname} {chr(127881)}"
        )
        return Message(
            receiver_id=update.object.peer_id,
            text=message_text,
            keyboard=START_CONTEST_KEYBOARD,
        )

    async def _history(
        self,
        update: Update,
        vote_id: Optional[str] = None,
        contest: Optional[ContestModel] = None,
    ) -> Message:
        """Возвращает победителя"""
        message_text = (
            f"{Info.LAST_WINNER} {contest.winner}"
            if hasattr(contest, "winner")
            else f"{Info.EMPTY_WINNER}"
        )
        return Message(
            receiver_id=update.object.peer_id,
            text=message_text,
            keyboard=START_CONTEST_KEYBOARD,
        )

    async def _get_score(
        self,
        update: Update,
        vote_id: Optional[str] = None,
        contest: Optional[ContestModel] = None,
    ) -> Message:
        """Список активных участников"""
        message_text = (
            f"{Info.LIST_ACTIVE_MEMBERS} {await self.tournament.get_table(contest)}"
        )
        return Message(
            receiver_id=update.object.peer_id,
            text=message_text,
            keyboard=CONTEST_KEYBOARD,
        )

    async def _help(
        self,
        update: Update,
        vote_id: Optional[str] = None,
        contest: Optional[ContestModel] = None,
    ) -> Message:
        return Message(
            receiver_id=update.object.peer_id,
            text=Info.GAME_HELP,
            keyboard=START_CONTEST_KEYBOARD,
        )

    async def _rules(
        self,
        update: Update,
        vote_id: Optional[str] = None,
        contest: Optional[ContestModel] = None,
    ) -> Message:
        return Message(
            receiver_id=update.object.peer_id,
            text=Info.GAME_RULES,
            keyboard=START_CONTEST_KEYBOARD,
        )

    async def _statistic(
        self,
        update: Update,
        vote_id: Optional[str] = None,
        contest: Optional[ContestModel] = None,
    ) -> Message:
        message_text = (
            f"{Info.STATISTICS} {await self.tournament.get_statistic(contest)}"
        )
        return Message(
            receiver_id=update.object.peer_id,
            text=message_text,
            keyboard=START_CONTEST_KEYBOARD,
        )
