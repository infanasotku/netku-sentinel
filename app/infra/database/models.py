from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

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
    phone: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)

    engine_subscriptions: Mapped[list["EngineSubscription"]] = relationship(
        "EngineSubscription", cascade="all, delete"
    )

    def __str__(self) -> str:
        return f"{self.username} [{self.email}]"


class EngineSubscription(BaseWithPK):
    __tablename__ = "engine_subscriptions"

    subscriber_id: Mapped[uuidpk] = mapped_column(ForeignKey("subscribers.id"))
    subscriber: Mapped[Subscriber] = relationship(
        Subscriber, back_populates="engine_subscriptions"
    )

    channel: Mapped[str]  # telegram
    endpoint: Mapped[str] = mapped_column(nullable=True)  # chat_id for telegram
    active: Mapped[bool] = mapped_column(default=True)
    event_type: Mapped[str]
    engine_host: Mapped[str]
