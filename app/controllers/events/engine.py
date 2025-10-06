from datetime import datetime
from logging import Logger
from uuid import UUID

from faststream.rabbit import RabbitRouter
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel

from app.container import Container
from app.infra.rabbit.queue import proxy_engine_queue

router = RabbitRouter()


class EngineEvent(BaseModel):
    id: UUID
    event_type: str
    aggregate_id: UUID
    version: str
    occurred_at: datetime
    payload: dict


@inject
def _get_logger(logger: Logger = Provide[Container.logger]):
    return logger


@router.subscriber(proxy_engine_queue)
async def handle_engine_events(event: EngineEvent):
    logger = _get_logger()
    logger.info(
        f"Processed event [{event.event_type}] for engine [{event.aggregate_id}] event_id [{event.id}]",
        extra=dict(queue=proxy_engine_queue.name),
    )
