from typing import Awaitable, TypeVar

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dependency_injector import containers, providers
from faststream.rabbit import RabbitBroker
from faststream.rabbit.publisher.asyncapi import AsyncAPIPublisher
from faststream.redis import RedisBroker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infra.database.uow import PgEngineUnitOfWork
from app.infra.logging import logger
from app.infra.rabbit.broker import get_publisher, get_rabbit_broker
from app.infra.rabbit.queue import sentinel_dead_letter_queue
from app.infra.redis.broker import get_redis, get_redis_broker
from app.services.engine import EngineEventService


def get_bot(token: str):
    return Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


ResourceT = TypeVar("ResourceT")


class EventsResource(providers.Resource[ResourceT]):
    pass


class BotResource(providers.Resource[ResourceT]):
    pass


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger = providers.Object(logger)

    async_engine = providers.Singleton(
        create_async_engine,
        config.postgres.dsn,
        connect_args=providers.Dict(
            server_settings=providers.Dict(search_path=config.postgres.sql_schema)
        ),
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    async_sessionmaker = providers.Singleton(
        async_sessionmaker[AsyncSession], async_engine
    )
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
        virtualhost=config.rabbit_proxy_vhost,
        logger=logger,
    )
    dlq_publisher = EventsResource[Awaitable[AsyncAPIPublisher]](
        get_publisher, rabbit_broker, queue=sentinel_dead_letter_queue
    )

    engine_uow = providers.Factory(PgEngineUnitOfWork, async_sessionmaker)

    engine = providers.Factory(
        EngineEventService,
        engine_uow,
    )
