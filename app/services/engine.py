from app.infra.database.uow import PgEngineUnitOfWork
from app.schemas.engine import EngineDeadCmd, EngineRestoredCmd, EngineUpdatedCmd


class EngineService:
    def __init__(self, uow: PgEngineUnitOfWork) -> None:
        self.uow = uow

    async def on_updated(self, cmd: EngineUpdatedCmd):
        async with self.uow.begin() as uow:
            if not await uow.inbox.try_record(cmd.id):
                return

    async def on_dead(self, cmd: EngineDeadCmd):
        pass

    async def on_restored(self, cmd: EngineRestoredCmd):
        pass
