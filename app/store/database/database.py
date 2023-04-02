import asyncio
import logging
from typing import Optional, TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.store.database.sqlalchemy_base import db
from app.web.config import Config

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, cfg: Config, app: Optional["Application"] = None):
        self.app = app
        self.config = cfg
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db
        db_url = self._build_url()
        self._engine = create_async_engine(db_url, echo=True, future=True)
        self.session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

    async def disconnect(self, *_: list, **__: dict) -> None:
        if self._engine:
            await self._engine.dispose()

    def _build_url(self) -> str:
        dialect = "postgresql"
        driver = "asyncpg"
        user = self.config.database.user
        password = self.config.database.password
        host = self.config.database.host
        port = self.config.database.port
        bd_name = self.config.database.database
        url = f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{bd_name}"
        return url
