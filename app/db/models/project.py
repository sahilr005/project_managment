from __future__ import annotations
import enum, uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, IdMixin, TimestampMixin, OrgScopedMixin

class ProjectStatus(str, enum.Enum):
    active = "active"
    archived = "archived"

class Project(Base, IdMixin, TimestampMixin, OrgScopedMixin):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("org_id", "key", name="uq_projects_org_key"),
        Index("ix_projects_org_created", "org_id", "created_at"),
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    key: Mapped[str]  = mapped_column(String(16), nullable=False)  # e.g., "ACME"
    status: Mapped[str] = mapped_column(String(16), default=ProjectStatus.active.value, nullable=False)
