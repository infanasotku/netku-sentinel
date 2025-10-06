from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel

from app.schemas.event import BaseEvent


class EngineStatus(StrEnum):
    ACTIVE = "active"
    READY = "ready"
    DEAD = "dead"


class EngineDeadCmd(BaseEvent):
    pass


class EngineUpdatedPayload(BaseModel):
    new_uuid: UUID | None
    new_status: EngineStatus


class EngineUpdatedCmd(BaseEvent):
    payload: EngineUpdatedPayload


class EngineRestoredPayload(BaseModel):
    uuid: UUID | None
    status: EngineStatus


class EngineRestoredCmd(BaseEvent):
    payload: EngineRestoredPayload
