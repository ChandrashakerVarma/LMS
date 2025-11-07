"""create attendances table

Revision ID: dc8c7d8f36ef
Revises: 5bcc9b263b2c
Create Date: 2025-11-05 16:36:10.012987
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc8c7d8f36ef'
down_revision: Union[str, Sequence[str], None] = '5bcc9b263b2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Create attendances table."""
    op.create_table(
        'attendances',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('shift_id', sa.Integer, sa.ForeignKey('shifts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('punch_in', sa.DateTime, nullable=False),
        sa.Column('punch_out', sa.DateTime, nullable=False),
        sa.Column('total_worked_minutes', sa.Integer, nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('NOW()')),
    )


def downgrade() -> None:
    """Downgrade schema: Drop attendances table."""
    op.drop_table('attendances')
