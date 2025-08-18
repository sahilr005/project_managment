from __future__ import annotations
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,Integer,Text,Index
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID
from app.db.base import Base,IdMixin,TimestampMixin,OrgScopedMixin

class File(Base,IdMixin,TimestampMixin,OrgScopedMixin):
    __tablename__="files"
    __table_args__=(
        Index("ix_files_org_created","org_id","created_at"),
    )

    storage: Mapped[str] = mapped_column(String(16),nullable=False,default="local")
    path: Mapped[str]= mapped_column(Text,nullable=False)
    content_type: Mapped[str|None] =mapped_column(String(128))
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sha256: Mapped[str | None] = mapped_column(String(64))

    # scan_status: pending|clean|infected|error
    scan_status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")