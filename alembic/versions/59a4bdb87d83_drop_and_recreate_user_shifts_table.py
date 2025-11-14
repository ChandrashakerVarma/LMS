"""drop and recreate user_shifts table

Revision ID: 59a4bdb87d83
Revises: d07f09161d8c
Create Date: 2025-11-10 12:40:15.630042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59a4bdb87d83'
down_revision: Union[str, Sequence[str], None] = 'd07f09161d8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop the table if it exists
    op.drop_table('user_shifts')

    # Recreate the table
    op.create_table(
        'user_shifts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('shift_id', sa.Integer, sa.ForeignKey('shifts.id'), nullable=False),
        sa.Column('assigned_date', sa.Date, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
    )

def downgrade():
    op.drop_table('user_shifts')