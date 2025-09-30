"""Add branch_id to users

Revision ID: 744af3d0edbd
Revises: 7d12f8271ba0
Create Date: 2025-09-26 15:18:29.134553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '744af3d0edbd'
down_revision: Union[str, Sequence[str], None] = '7d12f8271ba0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add branch_id column
    op.add_column('users', sa.Column(
        'branch_id', sa.Integer(), nullable=True
    ))
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_users_branch_id',  # constraint name
        'users',               # source table
        'branches',            # referent table
        ['branch_id'],         # local columns
        ['id'],                # remote columns
        ondelete='SET NULL'
    )


def downgrade():
    # Drop foreign key first
    op.drop_constraint('fk_users_branch_id', 'users', type_='foreignkey')
    # Drop column
    op.drop_column('users', 'branch_id')