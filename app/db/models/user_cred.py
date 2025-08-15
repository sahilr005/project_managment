from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean, Index
from app.db.base import Base, IdMixin, TimestampMixin
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as _UUID

class UserCredential(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_credentials"
    user_id: Mapped[_UUID] = mapped_column(UUID(as_uuid=True), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # optional email verification flags later
