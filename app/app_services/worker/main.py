from app.web.config import config
from bot_commands import BotWorker
from runner import run

if __name__ == "__main__":
    worker = BotWorker(cfg=config)
    run(start_tasks=[worker.start], stop_tasks=[worker.stop])
