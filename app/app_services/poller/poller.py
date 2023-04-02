import asyncio
import logging

from asyncio import Task, Future
from dataclasses import asdict

from typing import Optional

from aiohttp import ClientOSError

from app.app_services.pika_queue.rabbitMQ import RabbitMQ
from app.app_services.vk_api import VkApiAccessor
from app.app_services.vk_api import Update
from app.web.config import Config


class Poller:
    def __init__(self, cfg: Config):
        self.config = cfg
        self.is_running = False
        self.poll_task: Optional[Task] = None
        self.vk_api = VkApiAccessor(config=cfg)
        self.rabbitMQ = RabbitMQ(
            host=cfg.rabbitmq.host,
            port=cfg.rabbitmq.port,
            user=cfg.rabbitmq.user,
            password=cfg.rabbitmq.password,
        )
        self.logger = logging.getLogger("poller")

    def _done_callback(self, future: Future) -> None:
        if future.exception():
            self.logger.exception("polling failed", exc_info=future.exception())

    async def start(self) -> None:
        await self.vk_api.connect()
        task_poll = asyncio.create_task(self.poll())
        task_poll.add_done_callback(self._done_callback)
        self.is_running = True
        self.poll_task = task_poll
        await self.rabbitMQ.connect()

    async def transfer_update(self, updates: list[Update]) -> None:
        for update in updates:
            await self.rabbitMQ.send_event(message=asdict(update), routing_key="poller")
        await asyncio.sleep(1)

    async def stop(self) -> None:
        await self.vk_api.disconnect()
        self.is_running = False
        await self.rabbitMQ.disconnect()
        if self.poll_task:
            await asyncio.wait([self.poll_task], timeout=30)
            self.poll_task.cancel()
        self.poll_task = None

    async def poll(self) -> None:
        while self.is_running:
            try:
                updates = await self.vk_api.get_updates()
                await self.transfer_update(updates)
            except (ClientOSError, KeyError):
                continue
