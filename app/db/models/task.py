from __future__ import annotations
import enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, ForeignKey, Integer, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, IdMixin, TimestampMixin, OrgScopedMixin

class TaskStatus(str, enum.Enum):
    todo = "todo"
    doing = "doing"
    done = "done"

class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class Task(Base, IdMixin, TimestampMixin, OrgScopedMixin):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_org_proj_col", "org_id", "project_id", "column_id"),
        Index("ix_tasks_org_assignee", "org_id", "assignee_id"),
        Index("ix_tasks_org_created", "org_id", "created_at", "id"),
    )

    project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    board_id:   Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("boards.id", ondelete="SET NULL"), nullable=True)
    column_id:  Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("columns.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(16), default=TaskStatus.todo.value, nullable=False)
    priority: Mapped[str] = mapped_column(String(16), default=TaskPriority.medium.value, nullable=False)

    assignee_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    reporter_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

    due_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
