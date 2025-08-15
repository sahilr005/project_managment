from __future__ import annotations
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import Text,String,ForeignKey,UniqueConstraint,Index
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base,IdMixin,TimestampMixin,OrgScopedMixin

class Label(Base,IdMixin,TimestampMixin,OrgScopedMixin):
    __tablename__ = "labels"
    __table_args__=(
        UniqueConstraint("org_id", "project_id", "name", name="uq_labels_proj_name"),
        Index("ix_labels_org_proj", "org_id", "project_id"),
    )
    
    project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str]  = mapped_column(String(48), nullable=False)
    color: Mapped[str] = mapped_column(String(16), nullable=False, default="#808080")