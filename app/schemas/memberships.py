from __future__ import annotations
from pydantic import BaseModel,Field
from uuid import UUID
from datetime import datetime
from .common import ORMBase

class MembershipCreate(BaseModel):
    user_id: UUID
    role: str = Field(default="member",max_length=32)

class MembershipOut(ORMBase):
    org_id: UUID
    user_id: UUID
    role: str
    created_at: datetime
    updated_at: datetime
    