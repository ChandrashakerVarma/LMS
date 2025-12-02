"""add_department_id_and_is_org_admin_to_users

Revision ID: 43bb4af3bce5
Revises: b687f8ffbf27
Create Date: 2025-12-02 21:58:19.706059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '43bb4af3bce5'
down_revision: Union[str, Sequence[str], None] = 'b687f8ffbf27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Only add missing columns to users table
    op.add_column('users', sa.Column('department_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('is_org_admin', sa.Boolean(), nullable=True))
    op.create_foreign_key(None, 'users', 'departments', ['department_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'is_org_admin')
    op.drop_column('users', 'department_id')
