"""merge heads

Revision ID: f29d20bc21fc
Revises: 4d007e2d2fd0
Create Date: 2025-10-29 11:53:49.053215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f29d20bc21fc'
down_revision: Union[str, Sequence[str], None] = '4d007e2d2fd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
