from pydantic import BaseModel


class BotSettings(BaseModel):
    url: str
    token: str
    secret: str
