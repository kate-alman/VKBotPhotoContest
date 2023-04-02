from unittest.mock import patch

from .fixtures import *


async def test_poller_start_stop(poller):
    with patch.object(poller.rabbitMQ, "connect") as mock_connect:
        with patch.object(poller.rabbitMQ, "disconnect") as mock_disconnect:
            await poller.start()
            assert poller.poll_task is not None
            assert mock_connect.called
            await poller.stop()
            assert poller.poll_task is None
            assert mock_disconnect.called


async def test_poller_poll(poller, updates):
    with patch.object(poller.vk_api, "get_updates") as mock_get_updates:
        with patch.object(poller.rabbitMQ, "send_event") as mock_send_event:
            mock_get_updates.return_value = updates
            poller.is_running = True
            task = asyncio.create_task(poller.poll())
            await asyncio.sleep(1)
            poller.is_running = False
            task.cancel()
            assert mock_get_updates.called
            assert mock_send_event.called
