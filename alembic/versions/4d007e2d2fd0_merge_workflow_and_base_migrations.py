"""merge workflow and base migrations

Revision ID: 4d007e2d2fd0
Revises: 20251029_workflows, b6f4c8dae14c
Create Date: 2025-10-29 11:51:03.068409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d007e2d2fd0'
down_revision: Union[str, Sequence[str], None] = ('20251029_workflows', 'b6f4c8dae14c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
