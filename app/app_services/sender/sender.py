import asyncio
import logging

import bson
from aio_pika import IncomingMessage

from app.app_services.pika_queue import RabbitMQ
from app.app_services.vk_api import VkApiAccessor
from app.app_services.vk_api import Message
from app.web.config import Config


class VKSender:
    def __init__(self, cfg: Config):
        self.config = cfg
        self.workers = 15
        self.vk_api = VkApiAccessor(config=cfg)

        self.rabbitMQ = RabbitMQ(
            host=cfg.rabbitmq.host,
            port=cfg.rabbitmq.port,
            user=cfg.rabbitmq.user,
            password=cfg.rabbitmq.password,
        )
        self.routing_key_worker = "worker"
        self.routing_key_sender = "sender"
        self.queue_name = "vk_sender"
        self._tasks = []

        self.logger = logging.getLogger("sender")

    async def on_message(self, message: IncomingMessage) -> None:
        """Передает сообщения в обработку"""
        try:
            update = bson.loads(message.body)
            await self._handler_command(Message.from_dict(update))
            await message.ack()
        except KeyError:
            await message.ack()

    async def start(self) -> None:
        await self.vk_api.connect()
        await self.rabbitMQ.connect()
        self._tasks = [
            asyncio.create_task(self._worker_rabbit()) for _ in range(self.workers)
        ]

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        await self.vk_api.disconnect()
        await self.rabbitMQ.disconnect()

    async def _worker_rabbit(self) -> None:
        """Получает сообщений из очереди"""
        await self.rabbitMQ.listen_events(
            on_message_func=self.on_message,
            queue_name=self.queue_name,
            routing_key=[self.routing_key_sender],
        )

    async def _handler_command(self, message: Message) -> None:
        """В зависимости от наполнения сообщения, отправляет текст или вложения (фото)"""
        if message.text:
            await self.vk_api.send_group_message(
                Message(
                    receiver_id=message.receiver_id,
                    text=message.text,
                    keyboard=message.keyboard,
                ),
            )
        else:
            await self.vk_api.send_group_attachment_message(
                Message(
                    receiver_id=message.receiver_id,
                    text=message.text,
                    attachment=message.attachment,
                    keyboard=message.keyboard,
                ),
            )
