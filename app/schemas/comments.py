from __future__ import annotations
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from .common import ORMBase

class CommentCreate(BaseModel):
    task_id: UUID
    user_id: UUID | None = None
    body: str = Field(min_length=1)

class CommentOut(ORMBase):
    id: UUID
    org_id: UUID
    task_id: UUID
    user_id: UUID | None
    body: str
    created_at: datetime
    updated_at: datetime
