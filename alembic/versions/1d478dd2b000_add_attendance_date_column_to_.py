"""add attendance_date column to attendances

Revision ID: 1d478dd2b000
Revises: a096c4364161
Create Date: 2025-11-07 15:06:28.535498

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d478dd2b000'
down_revision: Union[str, Sequence[str], None] = 'a096c4364161'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
