from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

uuidpk = Annotated[
    UUID, mapped_column(SQLUUID(as_uuid=True), primary_key=True, default=uuid4)
]


class Base(DeclarativeBase): ...


class BaseWithPK(Base):
    __abstract__ = True

    id: Mapped[uuidpk]


class Inbox(Base):
    __tablename__ = "inbox"

    message_id: Mapped[uuidpk]
    received_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
    )


class Subscriber(BaseWithPK):
    __tablename__ = "subscribers"

    username: Mapped[str]
    email: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)
