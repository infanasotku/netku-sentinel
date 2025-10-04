from sqladmin import ModelView

from app.infra.database import models


class SubscriberView(ModelView, model=models.Subscriber):
    pass
