from enum import StrEnum

from sqladmin import ModelView
import wtforms

from app.infra.database import models
from app.schemas.subscription import EngineEventType, SubscriptionChannel


class SubscriberView(ModelView, model=models.Subscriber):
    can_export = False

    column_list = [
        models.Subscriber.id,
        models.Subscriber.username,
        models.Subscriber.phone,
        models.Subscriber.email,
        models.Subscriber.description,
        models.Subscriber.engine_subscriptions,
    ]
    form_columns = [
        models.Subscriber.username,
        models.Subscriber.phone,
        models.Subscriber.email,
        models.Subscriber.description,
    ]


def _enum_form_args(EnumType: type[StrEnum]):
    return dict(
        choices=[(c.value, c.name.replace("_", " ").title()) for c in EnumType],
        coerce=str,
    )


class EngineSubscriptionView(ModelView, model=models.EngineSubscription):
    can_export = False

    column_list = [
        models.EngineSubscription.id,
        models.EngineSubscription.subscriber,
        models.EngineSubscription.channel,
        models.EngineSubscription.endpoint,
        models.EngineSubscription.active,
        models.EngineSubscription.event_type,
        models.EngineSubscription.engine_host,
    ]

    form_args = dict(
        channel=_enum_form_args(SubscriptionChannel),
        event_type=_enum_form_args(EngineEventType),
        subscriber=dict(validators=[wtforms.validators.InputRequired()]),
    )
    form_overrides = dict(channel=wtforms.SelectField, event_type=wtforms.SelectField)
    form_columns = []
