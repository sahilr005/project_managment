from __future__ import annotations
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from .common import ORMBase

class ColumnCreate(BaseModel):
    board_id: UUID
    name: str = Field(min_length=1,max_length=80)
    order: int =0

class ColumnUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    order: int | None = None

class ColumnOut(ORMBase):
    id: UUID
    org_id: UUID
    board_id: UUID
    name: str
    order: int
    created_at: datetime
    updated_at: datetime