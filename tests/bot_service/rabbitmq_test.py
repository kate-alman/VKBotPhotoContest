from .fixtures import rabbitmq

from unittest.mock import AsyncMock, patch

import bson


async def test_connect_disconnect(rabbitmq):
    await rabbitmq.connect()
    assert rabbitmq.connection_ is not None
    await rabbitmq.disconnect()
    assert rabbitmq.connection_ is None


async def test_send_event(rabbitmq):
    await rabbitmq.connect()
    message = {"key": "value"}
    routing_key = "test"
    delay = 0
    await rabbitmq.send_event(message, routing_key, delay)
    assert rabbitmq.channel.publisher_confirms == 1
    await rabbitmq.disconnect()


async def test_on_message(rabbitmq):
    with patch.object(rabbitmq.logger, "info") as mock_logger:
        message = AsyncMock()
        text = {"key": "value"}
        message.body = bson.dumps(text)
        await rabbitmq.on_message(message)
        mock_logger.assert_called_once_with("Message body is: %r" % text)
