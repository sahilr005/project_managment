from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, IdMixin, TimestampMixin, OrgScopedMixin

class Board(Base, IdMixin, TimestampMixin, OrgScopedMixin):
    __tablename__ = "boards"
    __table_args__ = (
        UniqueConstraint("org_id", "project_id", "name", name="uq_boards_proj_name"),
        Index("ix_boards_org_proj", "org_id", "project_id"),
    )
    project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    type: Mapped[str] = mapped_column(String(16), default="kanban", nullable=False)  # kanban/scrum
