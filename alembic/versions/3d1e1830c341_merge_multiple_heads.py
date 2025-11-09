"""merge multiple heads

Revision ID: 3d1e1830c341
Revises: 5f15fee0bd76, b6b98d1800ed
Create Date: 2025-11-08 20:39:46.954205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d1e1830c341'
down_revision: Union[str, Sequence[str], None] = ('5f15fee0bd76', 'b6b98d1800ed')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
