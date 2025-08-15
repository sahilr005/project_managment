from __future__ import annotations
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from .common import ORMBase

class TaskCreate(BaseModel):
    project_id: UUID
    board_id: UUID | None = None
    column_id: UUID | None = None
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: str | None = "todo"
    priority: str | None = "medium"
    assignee_id: UUID | None = None
    reporter_id: UUID | None = None
    due_at: datetime | None = None
    rank: int | None = 0

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assignee_id: UUID | None = None
    reporter_id: UUID | None = None
    column_id: UUID | None = None
    due_at: datetime | None = None
    rank: int | None = None

class TaskOut(ORMBase):
    id: UUID
    org_id: UUID
    project_id: UUID
    board_id: UUID | None
    column_id: UUID | None
    title: str
    description: str | None
    status: str
    priority: str
    assignee_id: UUID | None
    reporter_id: UUID | None
    due_at: datetime | None
    rank: int
    created_at: datetime
    updated_at: datetime
