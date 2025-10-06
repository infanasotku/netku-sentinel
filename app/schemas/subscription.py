from enum import StrEnum


class SubscriptionChannel(StrEnum):
    TELEGRAM = "telegram"


# Engine
class EngineEventType(StrEnum):
    ENGINE_UPDATED = "engine_updated"
    ENGINE_DEAD = "engine_dead"
    ENGINE_RESTORED = "engine_restored"
