from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import UUID as _UUID
from app.db.base import Base, IdMixin, TimestampMixin, OrgScopedMixin

class Webhook(Base, IdMixin, TimestampMixin, OrgScopedMixin):
    __tablename__ = "webhooks"
    __table_args__ = (Index("ix_webhooks_org_active", "org_id", "active"),)

    url: Mapped[str] = mapped_column(String(512), nullable=False)
    secret: Mapped[str] = mapped_column(String(128), nullable=False)  # rotate-able, stored as plain here (use KMS/secret mgr in prod)
    events: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)  # list of event types
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
