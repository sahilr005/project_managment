"""add_updated_at_to_timestamp_mixin

Revision ID: 062b4e59520a
Revises: 237de525dbea
Create Date: 2025-08-14 23:21:56.068089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '062b4e59520a'
down_revision: Union[str, Sequence[str], None] = '237de525dbea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make idempotent: add columns only if they do not already exist
    op.execute("ALTER TABLE memberships ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();")
    op.execute("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();")


def downgrade() -> None:
    """Downgrade schema."""
    # Make idempotent
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS updated_at;")
    op.execute("ALTER TABLE organizations DROP COLUMN IF EXISTS updated_at;")
    op.execute("ALTER TABLE memberships DROP COLUMN IF EXISTS updated_at;")
