from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

uuidpk = Annotated[
    UUID, mapped_column(SQLUUID(as_uuid=True), primary_key=True, default=uuid4)
]


class Base(DeclarativeBase):
    id: Mapped[uuidpk]


class Inbox(DeclarativeBase):
    __tablename__ = "inbox"

    message_id: Mapped[uuidpk] = mapped_column()
    received_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
    )
