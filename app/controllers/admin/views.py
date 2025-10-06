from enum import StrEnum

from sqladmin import ModelView
import wtforms

from app.infra.database import models
from app.schemas.subscription import EngineEventType, SubscriptionChannel


def _restrict_spaces():
    return dict(validators=[wtforms.validators.Regexp(r"^[^\s]+$")])


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
    column_searchable_list = [models.Subscriber.username, models.Subscriber.email]

    form_columns = [
        models.Subscriber.username,
        models.Subscriber.phone,
        models.Subscriber.email,
        models.Subscriber.description,
    ]
    form_overrides = dict(email=wtforms.EmailField)
    form_args = dict(username=_restrict_spaces(), phone=_restrict_spaces())


def _enum_form_args(EnumType: type[StrEnum]):
    return dict(
        choices=[(c.value, c.name.replace("_", " ").title()) for c in EnumType],
        coerce=str,
    )


class EngineSubscriptionView(ModelView, model=models.EngineSubscription):
    can_export = False

    column_list = [
        models.EngineSubscription.subscriber,
        models.EngineSubscription.channel,
        models.EngineSubscription.endpoint,
        models.EngineSubscription.active,
        models.EngineSubscription.event_type,
        models.EngineSubscription.engine_host,
    ]
    column_searchable_list = [models.EngineSubscription.subscriber]

    form_args = dict(
        channel=_enum_form_args(SubscriptionChannel),
        event_type=_enum_form_args(EngineEventType),
        subscriber=dict(validators=[wtforms.validators.InputRequired()]),
    )
    form_overrides = dict(channel=wtforms.SelectField, event_type=wtforms.SelectField)
    form_columns = []
