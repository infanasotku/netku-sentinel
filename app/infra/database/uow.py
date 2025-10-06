from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncIterator, Generic, TypeVar

from sentry_sdk import start_span
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncSessionTransaction,
    async_sessionmaker,
)

from app.infra.database.repositories.inbox import PgInboxRepository


class PgUnitOfWorkContext:
    """Lightweight holder for a single DB transaction context.

    Contains the opened `AsyncSession` and the in-flight SQLAlchemy transaction.
    Concrete UnitOfWork implementations can subclass this context to expose
    repository gateways bound to the `session` (e.g. `inbox`, `users`, etc.).
    """

    def __init__(
        self, *, session: AsyncSession, transaction: AsyncSessionTransaction
    ) -> None:
        self._session = session
        self._transaction = transaction


ContextT = TypeVar("ContextT", bound=PgUnitOfWorkContext)


class PgUnitOfWork(ABC, Generic[ContextT]):
    """Minimal API to demarcate a single database transaction.

    What it provides
    - Opens a new AsyncSession and transaction and returns a context.
    - `begin()` is an async context manager that yields a context object
      (a `PgUnitOfWorkContext` or a subclass) and guarantees that all work
      inside the block commits atomically or rolls back on error.

    Usage
    >>> async with uow.begin() as ctx:
    ...     # use repositories exposed by the concrete context
    ...     # e.g. ctx.inbox.try_record(...)

    Notes
    - Keep transactions short — avoid network I/O while the transaction is
      open. Fetch external data before or after the block.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self._session_factory = session_factory

    @abstractmethod
    def _make_context(
        self, *, session: AsyncSession, transaction: AsyncSessionTransaction
    ) -> ContextT: ...

    async def _start(self) -> ContextT:
        session = self._session_factory()
        transaction = await session.begin()
        return self._make_context(session=session, transaction=transaction)

    async def _finish(self, exc: Exception | None, *, ctx: ContextT):
        try:
            if exc is None:
                await ctx._transaction.commit()
            else:
                raise exc
        except Exception:
            try:
                await ctx._session.rollback()
            except Exception:
                pass
            raise
        finally:
            await ctx._session.close()

    @asynccontextmanager
    async def begin(self) -> AsyncIterator[ContextT]:
        """Open a transaction and yield a UnitOfWork context.

        Guarantees commit on normal exit and rollback on exception, and always
        closes the session. The yielded context may be a specialized subclass
        exposing repositories.
        """
        with start_span(op="db", name="UOW transaction"):
            ctx = await self._start()
            try:
                yield ctx
            except Exception as e:
                await self._finish(e, ctx=ctx)
            else:
                await self._finish(None, ctx=ctx)


class PgEngineUnitOfWorkContext(PgUnitOfWorkContext):
    """Context for engine-related DB operations.

    Exposes repositories bound to the session (e.g., `inbox`).
    """

    def __init__(
        self, *, session: AsyncSession, transaction: AsyncSessionTransaction
    ) -> None:
        super().__init__(session=session, transaction=transaction)
        self.inbox = PgInboxRepository(session)


class PgEngineUnitOfWork(PgUnitOfWork[PgEngineUnitOfWorkContext]):
    def _make_context(
        self, *, session: AsyncSession, transaction: AsyncSessionTransaction
    ) -> PgEngineUnitOfWorkContext:
        return PgEngineUnitOfWorkContext(session=session, transaction=transaction)
