"""add audit fields to formula

Revision ID: 22e78e4be3b9
Revises: f9a86844b192
Create Date: 2025-11-21 12:33:55.790914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22e78e4be3b9'
down_revision: Union[str, Sequence[str], None] = 'f9a86844b192'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add new audit columns
    op.add_column("formulas", sa.Column("created_by", sa.String(length=100), nullable=True))
    op.add_column("formulas", sa.Column("modified_by", sa.String(length=100), nullable=True))


def downgrade():
    # Drop audit columns on downgrade
    op.drop_column("formulas", "modified_by")
    op.drop_column("formulas", "created_by")
