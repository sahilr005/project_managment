from __future__ import annotations
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class NotificationOut(BaseModel):
    id: UUID
    org_id: UUID
    user_id: UUID
    type: str
    payload: dict
    read: bool
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True

class PrefsIn(BaseModel):
    email_enabled: bool | None = None
    push_enabled: bool | None = None
    overrides: dict | None = None

class PrefsOut(BaseModel):
    id: UUID
    org_id: UUID
    user_id: UUID
    email_enabled: bool
    push_enabled: bool
    overrides: dict
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True
