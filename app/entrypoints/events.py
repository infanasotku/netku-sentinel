from contextlib import asynccontextmanager

from faststream.asgi import make_ping_asgi, AsgiFastStream, AsgiResponse, get

from app.infra.config import settings
from app.infra.logging import logger
from app.container import Container, EventsResource
from app.controllers.events import engine


def create_lifespan(container: Container, app: AsgiFastStream):
    async def _maybe_future(fut):
        if fut is not None:
            await fut

    @asynccontextmanager
    async def lifespan():
        engine_broker = await container.rabbit_broker()
        engine_broker.include_router(engine.router)

        @get
        async def lives(_):
            return AsgiResponse(b"", status_code=204)

        app.mount("/readyz", make_ping_asgi(engine_broker, timeout=5.0))
        app.mount("/livez", lives)
        app.broker = engine_broker

        await _maybe_future(container.init_resources(EventsResource))
        try:
            yield
        finally:
            await _maybe_future(container.shutdown_resources(EventsResource))

    return lifespan


def create_app():
    container = Container()
    container.config.from_pydantic(settings)
    container.wire(
        modules=[
            "app.controllers.events.engine",
        ]
    )

    app = AsgiFastStream(
        None,
        logger=logger,
        title="Sentinel events",
        version="",
        identifier="urn:events",
        asyncapi_path=None,
    )
    app.lifespan_context = create_lifespan(container, app)
    app.__dict__["container"] = container

    return app


app = create_app()
