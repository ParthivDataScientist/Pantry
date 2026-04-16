"""Pydantic schema for push notification subscription payloads."""

from pydantic import BaseModel, HttpUrl


class PushSubscriptionCreate(BaseModel):
    """Payload sent by the browser when subscribing to push notifications."""

    endpoint: HttpUrl
    keys: dict
