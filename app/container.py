from typing import Awaitable

from dependency_injector import providers, containers
from faststream.redis import RedisBroker
from aiogram.enums import ParseMode
from aiogram import Bot


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
    return Bot(token=token, parse_mode=ParseMode.HTML)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    redis_broker = providers.Resource[Awaitable[RedisBroker]](
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
