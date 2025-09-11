"""create enrollment table

Revision ID: ac9e9bc155f0
Revises: 0465e1581422
Create Date: 2025-09-11 14:25:12.706558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac9e9bc155f0'
down_revision: Union[str, Sequence[str], None] = '0465e1581422'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
