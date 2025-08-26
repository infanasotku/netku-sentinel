from typing import Awaitable, TypeVar

from dependency_injector import providers, containers
from faststream.redis import RedisBroker
from faststream.rabbit import RabbitBroker
from aiogram.enums import ParseMode
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from app.infra.redis.broker import get_redis, get_redis_broker
from app.infra.rabbit.broker import get_rabbit_broker


def get_bot(token: str):
    return Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


ResourceT = TypeVar("ResourceT")


class EventsResource(providers.Resource[ResourceT]):
    pass


class BotResource(providers.Resource[ResourceT]):
    pass


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    redis_broker = BotResource[Awaitable[RedisBroker]](
        get_redis_broker,  # type: ignore
        config.redis.dsn,
        db=config.redis.db,
    )
    redis = providers.Singleton(
        get_redis,
        redis_broker,
    )
    bot = providers.Singleton(
        get_bot,
        config.bot.token,
    )
    rabbit_broker = EventsResource[Awaitable[RabbitBroker]](
        get_rabbit_broker,  # type: ignore
        config.rabbit.dsn,
        virtualhost=config.rabbit.virtualhost,
    )
