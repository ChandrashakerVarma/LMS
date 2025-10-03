"""remove branch_id from organization

Revision ID: f5f011aadc63
Revises: 2bb544b81e38
Create Date: 2025-09-26 16:08:45.388957
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers
revision: str = 'f5f011aadc63'
down_revision: Union[str, Sequence[str], None] = '2bb544b81e38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    # Drop foreign key constraint if it exists
    fks = inspector.get_foreign_keys('organizations')
    for fk in fks:
        if 'branch_id' in fk['constrained_columns']:
            op.drop_constraint(fk['name'], 'organizations', type_='foreignkey')

    # Drop the branch_id column if it exists
    cols = [c['name'] for c in inspector.get_columns('organizations')]
    if 'branch_id' in cols:
        op.drop_column('organizations', 'branch_id')


def downgrade():
    # Add branch_id column back
    op.add_column(
        "organizations",
        sa.Column("branch_id", sa.Integer, nullable=True)
    )
    # Recreate foreign key
    op.create_foreign_key(
        None,  # let Alembic generate a name
        "organizations",
        "branches",
        ["branch_id"],
        ["id"],
        ondelete="SET NULL"
    )
