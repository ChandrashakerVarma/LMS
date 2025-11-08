"""add attendance_date column to attendances

Revision ID: 9d089a295cd1
Revises: dc2ae8ec8378
Create Date: 2025-11-07 14:32:45.019464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d089a295cd1'
down_revision: Union[str, Sequence[str], None] = 'dc2ae8ec8378'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('attendances', sa.Column('attendance_date', sa.Date(), nullable=False))


def downgrade():
    op.drop_column('attendances', 'attendance_date')
