"""Add is_org_admin column to users

Revision ID: 181582ffb259
Revises: 494a05653bbb
Create Date: 2025-12-03 12:37:21.695411
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '181582ffb259'
down_revision: Union[str, Sequence[str], None] = '494a05653bbb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""

    # --- SAFE ADD (DOES NOT FAIL IF COLUMN EXISTS) ---
    conn = op.get_bind()

    # Add is_org_admin if missing
    result = conn.execute(sa.text("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME='users' AND COLUMN_NAME='is_org_admin';
    """)).scalar()

    if result == 0:
        op.add_column('users', sa.Column('is_org_admin', sa.Boolean(), nullable=True))

    # Add deleted_at if missing
    result = conn.execute(sa.text("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME='users' AND COLUMN_NAME='deleted_at';
    """)).scalar()

    if result == 0:
        op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""

    # Safe drop
    conn = op.get_bind()

    result = conn.execute(sa.text("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME='users' AND COLUMN_NAME='is_org_admin';
    """)).scalar()
    if result == 1:
        op.drop_column('users', 'is_org_admin')

    result = conn.execute(sa.text("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME='users' AND COLUMN_NAME='deleted_at';
    """)).scalar()
    if result == 1:
        op.drop_column('users', 'deleted_at')
