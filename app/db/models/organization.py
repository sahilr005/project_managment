from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from app.db.base import Base,IdMixin,TimestampMixin

class Organization(Base,IdMixin,TimestampMixin):
    __tablename__ = "organizations"
    name: Mapped[str] = mapped_column(String(120),nullable=False)
    domain: Mapped[str| None] = mapped_column(String(255),nullable=True)