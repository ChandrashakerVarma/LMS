"""Merge multiple heads

Revision ID: c642d708939b
Revises: 7d54448aa394, e70ef9071ad1
Create Date: 2025-10-04 09:11:20.538672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c642d708939b'
down_revision: Union[str, Sequence[str], None] = ('7d54448aa394', 'e70ef9071ad1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
