"""empty message

Revision ID: cca4a1ed4520
Revises: b0383b11b97c
Create Date: 2025-08-30 13:07:01.355769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cca4a1ed4520'
down_revision: Union[str, Sequence[str], None] = 'b0383b11b97c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
