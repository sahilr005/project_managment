from __future__ import annotations
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from .common import ORMBase

class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    key: str = Field(min_length=2, max_length=16)

class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    status: str | None = Field(default=None)

class ProjectOut(ORMBase):
    id: UUID
    org_id: UUID
    name: str
    key: str
    status: str
    created_at: datetime
    updated_at: datetime
