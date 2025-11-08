"""merge multiple heads

Revision ID: 5f3ad464fd73
Revises: 1d478dd2b000, 9d089a295cd1
Create Date: 2025-11-07 15:09:47.733725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f3ad464fd73'
down_revision: Union[str, Sequence[str], None] = ('1d478dd2b000', '9d089a295cd1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
