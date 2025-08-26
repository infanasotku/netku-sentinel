from typing import Awaitable, TypeVar

from dependency_injector import providers, containers
from faststream.redis import RedisBroker
from aiogram.enums import ParseMode
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


async def get_redis_broker(dsn: str, *, db: int = 0):
    broker = RedisBroker(
        dsn,
        db=db,
        health_check_interval=10,
        retry_on_timeout=True,
        # Socket options
        socket_connect_timeout=5,
        socket_keepalive=True,
    )
    await broker.connect()
    try:
        yield broker
    finally:
        await broker.stop()


async def get_redis(broker: RedisBroker):
    return await broker.connect()


def get_bot(token: str):
    return Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


ResourceT = TypeVar("ResourceT")


class EventsResource(providers.Resource):
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
