import sys

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


def init():
    logger.remove()
    logger.add(
        sys.stderr,
        level="ERROR",
        format="<red>{time:YYYY-MM-DD HH:mm:ss.ms}</red> | <cyan>{file.path}:{line}:{function}</cyan> | <level>{message}</level>",
    )
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.ms}</green> | <cyan>{file.path}:{line}:{function}</cyan> | <level>{message}</level>",
    )


class Settings(BaseSettings):
    # Bot
    bot_token: str
    bot_username: str

    # Database
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str

    jwt_secret: str = ""

    # TON
    ton_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

    @property
    def sync_db_url(self) -> str:
        return f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"


settings = Settings()
