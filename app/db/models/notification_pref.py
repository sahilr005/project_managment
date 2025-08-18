from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import UUID as _UUID
from app.db.base import Base, IdMixin, TimestampMixin, OrgScopedMixin

class NotificationPreference(Base, IdMixin, TimestampMixin, OrgScopedMixin):
    __tablename__ = "notification_prefs"
    __table_args__ = (UniqueConstraint("org_id", "user_id", name="uq_notif_prefs_org_user"),)

    user_id: Mapped[_UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    push_enabled: Mapped[bool]  = mapped_column(Boolean, default=False, nullable=False)
    # optional: per-type overrides
    overrides: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
