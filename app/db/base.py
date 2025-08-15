from __future__ import annotations
import uuid
from sqlalchemy.orm import DeclarativeBase, declared_attr,Mapped,mapped_column
from sqlalchemy import MetaData,text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, func

convention = {
     "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)

class IdMixin:
    id: Mapped[uuid.UUID] = mapped_column (
        UUID(as_uuid=True),primary_key=True,
        default=uuid.uuid4
    )

class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class OrgScopedMixin:
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
