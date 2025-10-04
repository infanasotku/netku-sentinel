from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine

from app.container import Container
from app.controllers.admin.auth import AdminAuthenticationBackend
from app.controllers.admin.views import SubscriberView


@inject
def register_admin(
    app: FastAPI,
    *,
    username: str,
    password: str,
    secret: str,
    engine: AsyncEngine = Provide[Container.async_engine],
):
    authentication_backend = AdminAuthenticationBackend(
        secret, username=username, password=password
    )
    admin = Admin(
        app,
        engine,
        title="Engine panel",
        authentication_backend=authentication_backend,
        base_url="/",
    )

    admin.add_view(SubscriberView)
