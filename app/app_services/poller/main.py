from poller import Poller
from app.web.config import config
from runner import run

if __name__ == "__main__":
    poller = Poller(cfg=config)
    run(start_tasks=[poller.start], stop_tasks=[poller.stop])
