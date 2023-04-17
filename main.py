import os
import typing

from aiohttp.web_runner import AppRunner, TCPSite

from app.app_services.sender import VKSender
from app.app_services.worker.bot_commands import BotWorker
from app.web.app import setup_app
from app.web.config import config

from app.app_services.poller.poller import Poller

from runner import run

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Runner:
    def __init__(self, app_: "Application"):
        self.runner = AppRunner(app_)

    async def start(self) -> None:
        await self.runner.setup()
        site = TCPSite(self.runner, host=os.environ['APP_IP'], port=os.environ['APP_PORT'])
        await site.start()

    async def stop(self) -> None:
        await self.runner.cleanup()


app = setup_app()

if __name__ == "__main__":
    runner = Runner(app)
    poller = Poller(cfg=config)
    worker = BotWorker(cfg=config)
    sender = VKSender(cfg=config)
    run(
        start_tasks=[poller.start, worker.start, sender.start, runner.start],
        stop_tasks=[poller.stop, worker.stop, sender.stop, runner.stop],
    )
