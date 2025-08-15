from __future__ import annotations
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from .common import ORMBase

class LabelCreate(BaseModel):
    project_id: UUID
    name: str = Field(min_length=1, max_length=48)
    color: str = Field(default="#808080")

class LabelOut(ORMBase):
    id: UUID
    org_id: UUID
    project_id: UUID
    name: str
    color: str
    created_at: datetime
    updated_at: datetime
