from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as _UUID
from app.db.base import Base, IdMixin, TimestampMixin, OrgScopedMixin

class WebhookAttempt(Base, IdMixin, TimestampMixin, OrgScopedMixin):
    __tablename__ = "webhook_attempts"
    __table_args__ = (Index("ix_wh_attempts_org_hook_created", "org_id", "webhook_id", "created_at"),)

    webhook_id: Mapped[_UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(48), nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    # store a small excerpt of payload if you want (not required)
