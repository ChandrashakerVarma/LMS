"""drop permissions table

Revision ID: e4b449179ede
Revises: 0629898321f6
Create Date: 2025-10-31 11:24:44.737363
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4b449179ede'
down_revision: Union[str, Sequence[str], None] = '0629898321f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: drop permissions table."""
    op.drop_table('permissions')


def downgrade() -> None:
    """Downgrade schema: recreate permissions table."""
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('permission_type', sa.String(50), nullable=False),
        sa.Column('reason', sa.String(255), nullable=True),
    )


