from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseEvent(BaseModel):
    id: UUID
    aggregate_id: UUID
    version: str
    event_type: str
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)
