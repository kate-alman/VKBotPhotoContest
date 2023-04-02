import typing

from app.store.database.database import Database

from app.web.config import Config

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application", db: Database):
        from app.store.admin.accessor import AdminAccessor
        from app.store.contest.accessor import ContestAccessor

        self.admins = AdminAccessor(app)
        self.contest = ContestAccessor(db)
        self.app = app


def setup_store(app: "Application", cfg: Config):
    app.database = Database(app=app, cfg=cfg)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app, app.database)
