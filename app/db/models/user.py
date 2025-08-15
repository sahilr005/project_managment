from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String,Boolean
from app.db.base import Base,IdMixin,TimestampMixin

class User(Base,IdMixin,TimestampMixin):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255),unique=True,index=True,nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)
    