"""merge final heads

Revision ID: final_merge
Revises: 2277e8b40676, dbc68a92b6f0
Create Date: 2025-12-08 16:23:36.527670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'final_merge'
down_revision = ('2277e8b40676', 'dbc68a92b6f0')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
