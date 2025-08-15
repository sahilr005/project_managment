from __future__ import annotations
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,DateTime,Boolean,Index
from app.db.base import Base,IdMixin,TimestampMixin
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as _UUID

class UserSession(Base,IdMixin,TimestampMixin):
    __tablename__="user_sessions"
    user_id: Mapped[_UUID]= mapped_column(UUID(as_uuid=True),index=True,nullable=False)
    # refresh token rotation identifiers (opaque)
    refresh_token_hash: Mapped[str] = mapped_column(String(255),nullable=False)
    user_agent: Mapped[str|None]= mapped_column(String(255),nullable=True)
    ip: Mapped[str|None]= mapped_column(String(64),nullable=True)
    expires_at: Mapped[DateTime]=mapped_column(DateTime(timezone=True),nullable=False)
    revoked: Mapped[bool]= mapped_column(Boolean,default=False,nullable=False)
    __table_args__ = (Index("ix_user_sessions_user_expires", "user_id", "expires_at"),)
