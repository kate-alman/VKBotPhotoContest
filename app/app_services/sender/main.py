from sender import VKSender
from app.web.config import config
from runner import run

if __name__ == "__main__":
    sender = VKSender(cfg=config)
    run(start_tasks=[sender.start], stop_tasks=[sender.stop])
