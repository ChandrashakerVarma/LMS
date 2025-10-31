"""merge heads

Revision ID: b6f4c8dae14c
Revises: 31bb818d3c6d, 20251029_job_roles
Create Date: 2025-10-29 11:32:42.184431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6f4c8dae14c'
down_revision: Union[str, Sequence[str], None] = ('31bb818d3c6d', '20251029_job_roles')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
