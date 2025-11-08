"""remove user_id from salary_structures

Revision ID: dc2ae8ec8378
Revises: 3293ac269643
Create Date: 2025-11-06 15:22:45.251439

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc2ae8ec8378'
down_revision: Union[str, Sequence[str], None] = '3293ac269643'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
