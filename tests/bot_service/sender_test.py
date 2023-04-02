from app.app_services.vk_api import Message
from unittest.mock import patch

from .fixtures import sender, message_sender

import bson


async def test_on_message(sender, message_sender):
    update = {
        "receiver_id": 2000000003,
        "text": "Hello sweetie",
        "attachment": None,
        "keyboard": None,
    }
    message_sender.body = bson.dumps(update)
    with patch.object(sender, "_handler_command") as mock_handle:
        await sender.on_message(message_sender)
        assert mock_handle.called
        mock_handle.assert_called_once_with(Message.from_dict(update))
    assert message_sender.ack.called


async def test_start_stop_sender_rabbit(sender):
    with patch.object(sender.rabbitMQ, "connect") as mock_connect, patch.object(
        sender, "_worker_rabbit"
    ), patch.object(sender.rabbitMQ, "disconnect") as mock_disconnect:
        await sender.start()
        assert mock_connect.called
        assert len(sender._tasks) == sender.workers
        await sender.stop()
        assert all(task_.cancelled() for task_ in sender._tasks)
        assert mock_disconnect.called


async def test_worker_rabbit(sender):
    with patch.object(sender.rabbitMQ, "listen_events") as mock_listen:
        await sender._worker_rabbit()
        assert mock_listen.called
        mock_listen.assert_called_once_with(
            on_message_func=sender.on_message,
            queue_name=sender.queue_name,
            routing_key=[sender.routing_key_sender],
        )


async def test_send_group_message(sender):
    chat_id = 2000008796
    text = "Test message"
    message = Message(
        receiver_id=chat_id,
        text=text,
        attachment=None,
        keyboard=None,
    )
    with patch.object(sender.vk_api, "send_group_message") as mock_send:
        await sender._handler_command(message)
        assert mock_send.called
        mock_send.assert_called_once_with(message)
