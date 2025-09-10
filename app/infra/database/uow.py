from contextlib import asynccontextmanager

from sentry_sdk import start_span
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infra.database.repositories.inbox import PgInboxRepository


class PgUnitOfWork:
    """
    Defines the minimal API to demarcate a database transaction.

    Responsibilities
    ----------------
    - Provide `begin()` yielding an async context manager that encloses a *single* database transaction.
    - Ensure that all work inside the context either **commits** or **rolls back** together.

    Notes
    -----
    - Keep transactions short — do not perform network I/O while the transaction is open.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self._session_factory = session_factory

    async def start(self):
        self._session = self._session_factory()
        self._transaction = await self._session.begin()

    async def _finish(self, exc: Exception | None):
        try:
            if exc is None:
                await self._transaction.commit()
            else:
                await self._transaction.rollback()
        except Exception:
            await self._transaction.rollback()
            raise
        finally:
            await self._session.close()

    @asynccontextmanager
    async def begin(self):
        with start_span(op="db", name="Begin UOW"):
            await self.start()
            try:
                yield self
            except Exception as e:
                await self._finish(e)
                raise
            else:
                await self._finish(None)


class PgEngineUnitOfWork(PgUnitOfWork):
    async def start(self):
        await super().start()
        self.inbox = PgInboxRepository(self._session)
