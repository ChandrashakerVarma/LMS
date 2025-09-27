"""Add created_at and updated_at to organization

Revision ID: 7d12f8271ba0
Revises: a532927ff46c
Create Date: 2025-09-26 15:12:49.627516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d12f8271ba0'
down_revision: Union[str, Sequence[str], None] = 'a532927ff46c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Add created_at column
    op.add_column('organizations', sa.Column(
        'created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    ))
    # Add updated_at column
    op.add_column('organizations', sa.Column(
        'updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    ))


def downgrade():
    # Drop columns if rollback
    op.drop_column('organizations', 'updated_at')
    op.drop_column('organizations', 'created_at')
