from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, IdMixin, TimestampMixin, OrgScopedMixin

class Column(Base, IdMixin, TimestampMixin, OrgScopedMixin):
    __tablename__ = "columns"
    __table_args__ = (
        UniqueConstraint("org_id", "board_id", "name", name="uq_columns_board_name"),
        Index("ix_columns_org_board", "org_id", "board_id"),
        Index("ix_columns_org_order", "org_id", "order"),
    )
    board_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
