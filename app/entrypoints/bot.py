from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Header
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import DefaultKeyBuilder

from app.infra.config import settings
from app.container import Container, BotResource
from app.controllers.bot.main import COMMANDS, router


def create_lifespan(container: Container):
    async def _maybe_future(fut):
        if fut is not None:
            await fut

    @asynccontextmanager
    async def lifespan(app):
        await _maybe_future(container.init_resources(BotResource))
        bot = container.bot()
        redis = await container.redis()
        dp = Dispatcher(
            storage=RedisStorage(redis=redis, key_builder=DefaultKeyBuilder())
        )
        dp.include_router(router)
        register_message_processor(
            app, bot=bot, dispatcher=dp, secret=settings.bot.secret
        )

        await bot.set_webhook(
            url=settings.bot.url,
            secret_token=settings.bot.secret,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
        )
        await bot.set_my_commands(COMMANDS)

        try:
            yield
        finally:
            await _maybe_future(container.shutdown_resources(BotResource))

    return lifespan


def create_app():
    container = Container()
    container.config.from_pydantic(settings)
    container.wire(
        modules=[
            "app.controllers.bot.main",
        ]
    )

    app = FastAPI(docs_url=None, redoc_url=None, lifespan=create_lifespan(container))

    return app


def register_message_processor(
    app: FastAPI, *, bot: Bot, dispatcher: Dispatcher, secret: str
):
    """Register webhook endpoint for telegram bot"""

    @app.post("/process_message")
    async def _(
        update: dict,
        x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
    ):
        if x_telegram_bot_api_secret_token != secret:
            return {"status": "error", "message": "Wrong secret token !"}
        try:
            answer = await dispatcher.feed_update(bot=bot, update=Update(**update))
            return answer
        except Exception:
            return


app = create_app()
