"""create categories table

Revision ID: bf71b3071930
Revises: 9b17195477ce
Create Date: 2025-09-27 13:55:29.737295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf71b3071930'
down_revision: Union[str, Sequence[str], None] = '9b17195477ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String(length=150), nullable=False, unique=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False)
    )

def downgrade():
    op.drop_table('categories')