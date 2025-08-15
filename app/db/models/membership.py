from __future__ import annotations
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base,TimestampMixin,IdMixin,OrgScopedMixin

class Membership(Base,IdMixin,TimestampMixin,OrgScopedMixin):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("org_id","user_id",name="uq_memberships_org_user"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),nullable=False)

    role: Mapped[str] = mapped_column(String(120),default="member",nullable=False)

    org_fk = mapped_column(ForeignKey("organizations.id",ondelete="CASCADE"))
    user_fk = mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
