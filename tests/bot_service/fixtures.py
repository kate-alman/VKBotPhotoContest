import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.app_services.pika_queue import RabbitMQ
from app.app_services.poller.poller import Poller
from app.app_services.sender import VKSender
from app.app_services.vk_api import Message, UpdateObject, Update
from app.web.config import config


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="function")
def chat_id():
    return 2000000002


@pytest.fixture(scope="function")
def member_id():
    return 41063300


@pytest.fixture(scope="function")
def message(chat_id):
    return Message(
        receiver_id=chat_id, text="Hello World!", attachment=None, keyboard=None
    )


@pytest.fixture(scope="function")
def update_object(chat_id, member_id) -> UpdateObject:
    return UpdateObject(
        id=1,
        peer_id=chat_id,
        user_id=member_id,
        body="PewPew",
    )


@pytest.fixture
def updates(chat_id, member_id, update_object):
    return Update(
        type="new_message",
        object=update_object,
    ), Update(
        type="new_event",
        object=update_object,
    )


def test_get_updates_response(updates):
    assert updates[0].type == "new_message" and updates[1].type == "new_event"
    assert len(updates) == 2


@pytest.fixture
def poller():
    return Poller(cfg=config)


@pytest.fixture
def rabbitmq():
    return RabbitMQ(
        host=config.rabbitmq.host,
        port=config.rabbitmq.port,
        user=config.rabbitmq.user,
        password=config.rabbitmq.password,
    )


@pytest.fixture(scope="session")
def sender():
    return VKSender(cfg=config)


@pytest.fixture
async def message_sender():
    message = MagicMock()
    message.ack = AsyncMock()
    return message
