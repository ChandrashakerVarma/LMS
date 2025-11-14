"""merge heads after pull

Revision ID: 4d43f29c963c
Revises: 5f3ad464fd73, e98879d4900d
Create Date: 2025-11-09 17:11:51.742409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d43f29c963c'
down_revision: Union[str, Sequence[str], None] = ('5f3ad464fd73', 'e98879d4900d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
