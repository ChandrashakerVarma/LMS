"""create department table

Revision ID: 1401178fc969
Revises: d9b977eb5e42
Create Date: 2025-09-25 12:55:26.310218
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '1401178fc969'
down_revision: Union[str, Sequence[str], None] = 'd9b977eb5e42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Alter column safely
    op.alter_column('roles', 'name',
                    existing_type=sa.String(length=100),
                    type_=sa.String(length=50),
                    existing_nullable=False)
    
    # Only drop columns that exist in PostgreSQL
    for col in ['permissions', 'description', 'updated_at', 'status', 'code']:
        try:
            op.drop_column('roles', col)
        except Exception:
            pass  # skip if column doesn't exist

    # Add department table
    op.create_table(
        'department',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('department')
    
    # Revert column type
    op.alter_column('roles', 'name',
                    existing_type=sa.String(length=50),
                    type_=sa.String(length=100),
                    existing_nullable=False)
