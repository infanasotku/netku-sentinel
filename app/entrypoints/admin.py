from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.container import Container
from app.controllers.admin.main import register_admin
from app.infra.config import settings


def create_app() -> FastAPI:
    container = Container()
    container.config.from_pydantic(settings)
    container.wire(
        modules=[
            "app.controllers.admin.main",
            "app.controllers.admin.views",
        ]
    )

    app = FastAPI()
    register_admin(
        app,
        username=settings.admin.username,
        password=settings.admin.password,
        secret=settings.admin.secret,
    )

    Instrumentator().instrument(app).expose(app)

    return app


app = create_app()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
