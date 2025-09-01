import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv

from app.infra.config.admin import AdminSettings
from app.infra.config.bot import BotSettings
from app.infra.config.postgres import PostgreSQLSettings
from app.infra.config.rabbitmq import RabbitMQSettings
from app.infra.config.redis import RedisSettings
from app.infra.config.sentry import SentrySettings


class Settings(BaseSettings):
    admin: AdminSettings
    postgres: PostgreSQLSettings
    rabbit: RabbitMQSettings
    redis: RedisSettings
    sentry: SentrySettings
    bot: BotSettings

    rabbit_proxy_vhost: str = Field()

    model_config = SettingsConfigDict(env_nested_delimiter="__")


def _generate_settings():
    load_dotenv(override=True, dotenv_path=os.getcwd() + "/.env")
    return Settings()  # type: ignore


settings = _generate_settings()
