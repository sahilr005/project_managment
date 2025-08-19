"""enable_rls_on_files_table

Revision ID: 3f493593f2f3
Revises: 1788569368d2
Create Date: 2025-01-16 22:10:17.893869

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3f493593f2f3'
down_revision: Union[str, Sequence[str], None] = '1788569368d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable RLS and create tenant isolation policy for files table
    op.execute("ALTER TABLE files ENABLE ROW LEVEL SECURITY;")
    op.execute("""
    CREATE POLICY tenant_isolation ON files
    USING (org_id::text = current_setting('app.current_org_id', true));
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop RLS policy and disable RLS for files table
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON files;")
    op.execute("ALTER TABLE files DISABLE ROW LEVEL SECURITY;")
