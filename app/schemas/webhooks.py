from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID
from datetime import datetime

class WebhookCreate(BaseModel):
    url: HttpUrl
    secret: str = Field(min_length=8, max_length=128)
    events: list[str]

class WebhookUpdate(BaseModel):
    url: HttpUrl | None = None
    secret: str | None = None
    events: list[str] | None = None
    active: bool | None = None

class WebhookOut(BaseModel):
    id: UUID
    org_id: UUID
    url: str
    events: list[str]
    active: bool
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True
