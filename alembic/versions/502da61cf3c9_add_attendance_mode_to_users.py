"""add attendance_mode to users

Revision ID: 502da61cf3c9
Revises: 14fe199f13ab
Create Date: 2025-12-04 13:00:05.586770
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '502da61cf3c9'
down_revision: Union[str, Sequence[str], None] = '14fe199f13ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add attendance_mode column"""
    op.add_column(
        'users',
        sa.Column('attendance_mode', sa.String(20), nullable=False, server_default="BRANCH")
    )


def downgrade() -> None:
    """Downgrade schema: remove attendance_mode column"""
    op.drop_column('users', 'attendance_mode')
