"""Merge 3 heads

Revision ID: d1afc39f6407
Revises: cbb8a888cb3b, e68fc44314c0
Create Date: 2025-12-03 19:18:32.009792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1afc39f6407'
down_revision = ('cbb8a888cb3b', 'e68fc44314c0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
