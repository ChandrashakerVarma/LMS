"""add_deleted_at_to_users

Revision ID: b687f8ffbf27
Revises: 55172c4efa98
Create Date: 2025-12-02 21:48:19.696583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'b687f8ffbf27'
down_revision: Union[str, Sequence[str], None] = '55172c4efa98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Only add deleted_at column
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'deleted_at')
