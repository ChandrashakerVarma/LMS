"""remove branch_id from organization

Revision ID: f5f011aadc63
Revises: 2bb544b81e38
Create Date: 2025-09-26 16:08:45.388957
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'f5f011aadc63'
down_revision: Union[str, Sequence[str], None] = '2bb544b81e38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # First drop the FK constraint if it exists
    op.execute("ALTER TABLE organizations DROP FOREIGN KEY organizations_ibfk_branch_id;")
    # Then drop the column
    op.execute("ALTER TABLE organizations DROP COLUMN branch_id;")

def downgrade():
    op.add_column(
        "organizations",
        sa.Column("branch_id", sa.Integer, sa.ForeignKey("branches.id"), nullable=True)
    )
