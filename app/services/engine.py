from app.schemas.engine import EngineDeadCmd, EngineRestoredCmd, EngineUpdatedCmd


class EngineEventService:
    async def on_updated(self, cmd: EngineUpdatedCmd):
        pass

    async def on_dead(self, cmd: EngineDeadCmd):
        pass

    async def on_restored(self, cmd: EngineRestoredCmd):
        pass
