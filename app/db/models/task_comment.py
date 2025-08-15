from __future__ import annotations
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import Text,ForeignKey,Index
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base,IdMixin,TimestampMixin,OrgScopedMixin


class TaskComment(Base,IdMixin,TimestampMixin,OrgScopedMixin):
    __tablename__= "task_comments"
    __table_args__ = (Index("ix_task_comments_org_task", "org_id", "task_id", "created_at"),)

    task_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    body: Mapped[str]     = mapped_column(Text, nullable=False)