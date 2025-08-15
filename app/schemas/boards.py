from __future__ import annotations
from pydantic import BaseModel,Field
from uuid import UUID
from datetime import datetime
from .common import ORMBase

class BoardCreate(BaseModel):
    project_id: UUID
    name: str = Field(min_length=2,max_length=80)
    type: str = Field(default="kanban")

class BoardOut(ORMBase):
    id: UUID
    org_id: UUID
    project_id: UUID
    name: str
    type: str
    created_at: datetime
    updated_at: datetime