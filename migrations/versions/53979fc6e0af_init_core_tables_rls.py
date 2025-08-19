"""init core tables + RLS

Revision ID: 53979fc6e0af
Revises: 062b4e59520a
Create Date: 2025-08-14 23:43:56.546019

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53979fc6e0af'
down_revision: Union[str, Sequence[str], None] = '062b4e59520a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Be tolerant if 'ord_id' doesn't exist
    op.execute("ALTER TABLE memberships DROP COLUMN IF EXISTS ord_id;")


def downgrade() -> None:
    """Downgrade schema."""
    # Only add if missing
    op.execute("ALTER TABLE memberships ADD COLUMN IF NOT EXISTS ord_id uuid NOT NULL;")
