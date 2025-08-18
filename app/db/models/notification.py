from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import UUID as _UUID
from app.db.base import Base, IdMixin, TimestampMixin, OrgScopedMixin

class Notification(Base, IdMixin, TimestampMixin, OrgScopedMixin):
    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_org_user_created", "org_id", "user_id", "created_at"),)

    user_id: Mapped[_UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    type: Mapped[str] = mapped_column(String(48), nullable=False)  # e.g., "task.created", "comment.created"
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
