from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, IdMixin, TimestampMixin, OrgScopedMixin

class TaskLabel(Base, IdMixin, TimestampMixin, OrgScopedMixin):
    __tablename__ = "task_labels"
    __table_args__ = (
        UniqueConstraint("org_id", "task_id", "label_id", name="uq_task_labels"),
        Index("ix_task_labels_org_task", "org_id", "task_id"),
    )
    task_id:  Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    label_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("labels.id", ondelete="CASCADE"), nullable=False)
