"""add audit fields to permissions

Revision ID: f9a86844b192
Revises: 6753a841fb47
Create Date: 2025-11-21 10:53:42.098380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func


# revision identifiers, used by Alembic.
revision: str = 'f9a86844b192'
down_revision: Union[str, Sequence[str], None] = '6753a841fb47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add created_at and updated_at
    op.add_column('permissions', sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True))
    op.add_column('permissions', sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True))

    # Add created_by and modified_by
    op.add_column('permissions', sa.Column('created_by', sa.String(length=100), nullable=True))
    op.add_column('permissions', sa.Column('modified_by', sa.String(length=100), nullable=True))


def downgrade():
    op.drop_column('permissions', 'modified_by')
    op.drop_column('permissions', 'created_by')
    op.drop_column('permissions', 'updated_at')
    op.drop_column('permissions', 'created_at')