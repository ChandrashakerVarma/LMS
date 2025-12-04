"""Add AI fields to attendance

Revision ID: eaec9ea4abcd
Revises: 181582ffb259
Create Date: 2025-12-03 14:04:36.592186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eaec9ea4abcd'
down_revision: Union[str, Sequence[str], None] = '181582ffb259'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
