"""add audit 

Revision ID: 38eb9d4ee3b7
Revises: 4943ba5e7c95
Create Date: 2025-11-20 17:14:02.650734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38eb9d4ee3b7'
down_revision: Union[str, Sequence[str], None] = '4943ba5e7c95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('leave_master', sa.Column('created_by', sa.String(length=100), nullable=True))
    op.add_column('leave_master', sa.Column('modified_by', sa.String(length=100), nullable=True))


def downgrade():
    op.drop_column('leave_master', 'modified_by')
    op.drop_column('leave_master', 'created_by')
