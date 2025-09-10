from logging import Logger
from typing import Any

from dependency_injector.wiring import Provide, inject
from faststream.rabbit import RabbitMessage, RabbitRouter

from app.container import Container
from app.infra.rabbit.queue import MAX_RETRY, proxy_engine_queue
from app.schemas.engine import EngineDeadCmd, EngineRestoredCmd, EngineUpdatedCmd
from app.schemas.event import BaseEvent
from app.services.engine import EngineEventService

router = RabbitRouter()


class EngineEvent(BaseEvent):
    payload: dict


@inject
def _get_logger(logger: Logger = Provide[Container.logger]):
    return logger


@inject
async def _get_event_service(
    event_service: EngineEventService = Provide[Container.engine],
):
    return event_service


def _retry_count(headers: dict[str, Any], retry_queue: str) -> int:
    deaths: list[dict[str, Any]] = headers.get("x-death", []) or []
    for d in deaths:
        if d.get("queue") == retry_queue:
            return int(d.get("count", 0))
    return 0


@router.subscriber(proxy_engine_queue)
async def handle_engine_events(event: EngineEvent, msg: RabbitMessage):
    logger = _get_logger()

    retry_count = _retry_count(msg.headers, proxy_engine_queue.name)
    if retry_count > MAX_RETRY:
        logger.warning(
            f"Event [{event.event_type}-{event.id}] exceeded max retry limit"
        )
        # Automatic ack
    else:
        await _handle(event)

    logger.info(
        f"Processed event [{event.event_type}] for engine [{event.aggregate_id}] event_id [{event.id}]",
        extra=dict(queue=proxy_engine_queue.name),
    )


@inject
async def _handle(
    event: EngineEvent,
    svc: EngineEventService = Provide[Container.engine],
):
    match event.event_type:
        case "EngineDead":
            await svc.on_dead(EngineDeadCmd.model_validate(event))
        case "EngineUpdated":
            await svc.on_updated(EngineUpdatedCmd.model_validate(event))
        case "EngineRestored":
            await svc.on_restored(EngineRestoredCmd.model_validate(event))
