"""create department table

Revision ID: 35a15b1ce4e4
Revises: 1401178fc969
Create Date: 2025-09-25 13:10:12.317194
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '35a15b1ce4e4'
down_revision: Union[str, Sequence[str], None] = '1401178fc969'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema safely for PostgreSQL."""

    # Safely alter column type if it exists
    op.alter_column(
        'roles', 'name',
        existing_type=sa.VARCHAR(length=100),
        type_=sa.String(length=50),
        existing_nullable=False
    )

    # Only drop columns if they exist
    with op.get_context().autocommit_block():
        conn = op.get_bind()
        for col in ['created_at', 'status', 'permissions', 'updated_at', 'description', 'code']:
            # Check if column exists
            result = conn.execute(
                sa.text(
                    f"SELECT column_name FROM information_schema.columns "
                    f"WHERE table_name='roles' AND column_name='{col}'"
                )
            ).fetchone()
            if result:
                op.drop_column('roles', col)

    # Only create department table if it does not exist
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT to_regclass('public.department')")).scalar()
    if not result:
        op.create_table(
            'department',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
        )

def downgrade() -> None:
    """Downgrade schema."""
    # Re-add dropped columns (optional)
    op.add_column('roles', sa.Column('code', sa.String(20), nullable=False))
    op.add_column('roles', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('roles', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('roles', sa.Column('permissions', sa.Text(), nullable=True))
    op.add_column('roles', sa.Column('status', sa.SmallInteger(), nullable=True))
    op.add_column('roles', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True))
    # Revert column type
    op.alter_column(
        'roles', 'name',
        existing_type=sa.String(length=50),
        type_=sa.String(length=100),
        existing_nullable=False
    )
    # Drop department table if exists
    op.drop_table('department')
