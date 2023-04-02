import os
import typing
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    email: str
    password: str


@dataclass
class BotConfig:
    token: str
    group_id: str


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "project"


@dataclass
class RabbitConfig:
    host: str = "localhost"
    port: str = "15672"
    user: str = "guest"
    password: str = "guest"


@dataclass
class Config:
    admin: AdminConfig
    session: SessionConfig = None
    bot: BotConfig = None
    database: DatabaseConfig = None
    rabbitmq: RabbitConfig = None


def setup_config(app: "Application"):
    app.config = config


env_name = ".env"

BASE_DIR = Path(__file__).resolve().parent.parent.parent

dotenv_file = os.path.join(BASE_DIR, env_name)
if os.path.isfile(dotenv_file):
    load_dotenv(dotenv_file)

config_env = os.environ

config = Config(
    admin=AdminConfig(
        email=config_env.get("ADMIN_EMAIL"), password=config_env.get("ADMIN_PASSWORD")
    ),
    session=SessionConfig(key=config_env.get("SESSION_KEY")),
    bot=BotConfig(
        token=config_env.get("BOT_TOKEN"),
        group_id=config_env.get("GROUP_ID"),
    ),
    database=DatabaseConfig(
        host=config_env.get("DATABASE_HOST"),
        port=int(config_env.get("DATABASE_PORT")),
        user=config_env.get("POSTGRES_USER"),
        password=config_env.get("POSTGRES_PASSWORD"),
        database=config_env.get("POSTGRES_DB"),
    ),
    rabbitmq=RabbitConfig(
        host=config_env.get("RABBITMQ_HOST"),
        port=config_env.get("RABBITMQ_PORT"),
        user=config_env.get("RABBITMQ_USER"),
        password=config_env.get("RABBITMQ_PASSWORD"),
    ),
)
