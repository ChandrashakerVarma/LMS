"""create roles table

Revision ID: 602426e31af6
Revises: e4b449179ede
Create Date: 2025-10-31 11:37:22.409010
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '602426e31af6'
down_revision: Union[str, Sequence[str], None] = 'e4b449179ede'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Skip creation if roles table already exists"""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'roles' not in inspector.get_table_names():
        op.create_table(
            'roles',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(length=50), nullable=False, unique=True),
        )



def downgrade() -> None:
    """Drop roles table"""
    op.drop_table('roles')
