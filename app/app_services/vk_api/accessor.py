import json
import logging
import random

from typing import Optional

from aiohttp import TCPConnector
from aiohttp.client import ClientSession
from aiohttp.web_exceptions import HTTPForbidden, HTTPNotFound

from app.contest.models import Member
from app.app_services.vk_api.dataclasses import Message, Update, UpdateObject
from app.web.config import Config


API_PATH = "https://api.vk.com/method/"


class VkApiAccessor:
    def __init__(self, config: Config):
        self.config = config
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.ts: Optional[int] = None
        self.logger = logging.getLogger("poller")

    async def connect(self) -> None:
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)

    async def disconnect(self) -> None:
        if self.session:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params["v"] = params.get("v", "5.131")
        url = f"{host}{method}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self) -> None:
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.config.bot.group_id,
                    "access_token": self.config.bot.token,
                },
            )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(self.server)

    async def reconnect(self) -> None:
        await self.disconnect()
        await self.connect()
        self.logger.info("reconnect done")

    @staticmethod
    def get_message_body(message: dict) -> str:
        if "action" in message and message["action"]["member_id"] < 0:
            return message["action"]["member_id"]
        if "payload" in message:
            return message["payload"]
        else:
            return message["text"]

    async def get_updates(self) -> list[Update]:
        async with self.session.get(
            self._build_query(
                host=self.server,
                method="",
                params={
                    "act": "a_check",
                    "key": self.key,
                    "ts": self.ts,
                    "wait": 30,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
            if "failed" in data:
                await self.reconnect()
            self.ts = data["ts"]
            raw_updates = data.get("updates", [])
            updates = []
            for update in raw_updates:
                message = update["object"]["message"]
                updates.append(
                    Update(
                        type=update["type"],
                        object=UpdateObject(
                            id=message["id"],
                            user_id=message["from_id"],
                            body=self.get_message_body(message),
                            peer_id=message["peer_id"],
                        ),
                    )
                )
            return updates

    async def send_message(self, message: Message) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "user_id": message.receiver_id,
                    "random_id": random.randint(1, 2**32),
                    "peer_id": "-" + str(self.config.bot.group_id),
                    "message": message.text,
                    "access_token": self.config.bot.token,
                    "keyboard": json.dumps(
                        [] if message.keyboard is None else message.keyboard
                    ),
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def send_group_message(self, message: Message) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "random_id": random.randint(1, 2**32),
                    "peer_id": message.receiver_id,
                    "message": message.text,
                    "access_token": self.config.bot.token,
                    "keyboard": json.dumps(
                        [] if message.keyboard is None else message.keyboard
                    ),
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def send_group_attachment_message(self, message: Message) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "random_id": random.randint(1, 2**32),
                    "peer_id": message.receiver_id,
                    "attachment": message.attachment,
                    "access_token": self.config.bot.token,
                    "keyboard": json.dumps(
                        [] if message.keyboard is None else message.keyboard
                    ),
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def get_conversation_members(self, peer_id: int) -> list[Member]:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.getConversationMembers",
                params={
                    "peer_id": peer_id,
                    "group_id": self.config.bot.group_id,
                    "access_token": self.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            if data.get("error"):
                if data.get("error").get("error_code") == 917:
                    raise HTTPForbidden(reason="Нет прав администратора")

            self.logger.info(data)
            users = data["response"]["profiles"]
            users_data = []
            for user in users:
                try:
                    users_data.append(
                        Member(
                            id=user["id"],
                            name=user["first_name"],
                            surname=user["last_name"],
                            photo=await self.get_user_photo(user["id"]),
                        )
                    )
                except HTTPNotFound:
                    continue
            return users_data

    async def get_user_photo(self, user_id: int) -> str:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "users.get",
                params={
                    "user_ids": user_id,
                    "access_token": self.config.bot.token,
                    "fields": "photo_id",
                },
            )
        ) as resp:
            try:
                data = await resp.json()
                self.logger.info(data)
                return data["response"][0]["photo_id"]
            except KeyError:
                raise HTTPNotFound(reason="У пользователя нет аватарки")
