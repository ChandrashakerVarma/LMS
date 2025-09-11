"""create enrollment table

Revision ID: 0465e1581422
Revises: 7857e4bd0437
Create Date: 2025-09-11 13:22:39.914222

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0465e1581422'
down_revision: Union[str, Sequence[str], None] = '7857e4bd0437'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
