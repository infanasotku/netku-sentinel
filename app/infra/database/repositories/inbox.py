from uuid import UUID

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.infra.database.models import Inbox
from app.infra.database.repositories.base import PgRepository


class PgInboxRepository(PgRepository):
    async def try_record(self, message_id: UUID) -> bool:
        """Attempt to persist an inbox record once.

        Returns `True` only when the record is inserted now (first time seen),
        and `False` when a row with the same primary key already exists.

        This is a concurrency-safe, idempotent guard for exactly-once handling
        of upstream messages/events, implemented via
        `INSERT ... ON CONFLICT (message_id) DO NOTHING RETURNING message_id`.
        """
        stmt = (
            pg_insert(Inbox)
            .values(message_id=message_id)
            .on_conflict_do_nothing(index_elements=[Inbox.message_id])
            .returning(Inbox.message_id)
        )
        inserted = await self._session.scalar(stmt)
        return inserted is not None
