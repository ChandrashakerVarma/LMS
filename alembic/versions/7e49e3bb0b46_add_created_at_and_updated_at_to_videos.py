"""add created_at and updated_at to videos

Revision ID: 7e49e3bb0b46
Revises: bd7f1fb274bf
Create Date: 2025-10-07 12:33:33.822906

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e49e3bb0b46'
down_revision: Union[str, Sequence[str], None] = 'bd7f1fb274bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('videos', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))
    op.add_column('videos', sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True))


def downgrade():
    op.drop_column('videos', 'created_at')
    op.drop_column('videos', 'updated_at')
