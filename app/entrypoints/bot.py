from contextlib import asynccontextmanager
from typing import Annotated

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Update
from fastapi import FastAPI, Header
from prometheus_fastapi_instrumentator import Instrumentator

from app.container import BotResource, Container
from app.controllers.bot.main import COMMANDS, router
from app.infra.config import settings


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

        # Check current webhook before setting a new one to avoid redundant
        # set_webhook calls from multiple pods starting simultaneously.
        try:
            webhook_info = await bot.get_webhook_info()
        except Exception:
            webhook_info = None

        if webhook_info is None or webhook_info.url != settings.bot.url:
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

    Instrumentator().instrument(app).expose(app)

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


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
