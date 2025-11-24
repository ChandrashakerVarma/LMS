"""add audit fields to leave_master

Revision ID: 6753a841fb47
Revises: 38eb9d4ee3b7
Create Date: 2025-11-20 17:20:44.917653
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '6753a841fb47'
down_revision: Union[str, Sequence[str], None] = '38eb9d4ee3b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    columns = [col["name"] for col in inspector.get_columns("leave_master")]

    # Add created_by if not exists
    if "created_by" not in columns:
        op.add_column(
            "leave_master",
            sa.Column("created_by", sa.String(length=100), nullable=True)
        )

    # Add modified_by if not exists
    if "modified_by" not in columns:
        op.add_column(
            "leave_master",
            sa.Column("modified_by", sa.String(length=100), nullable=True)
        )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    columns = [col["name"] for col in inspector.get_columns("leave_master")]

    # Drop modified_by if exists
    if "modified_by" in columns:
        op.drop_column("leave_master", "modified_by")

    # Drop created_by if exists
    if "created_by" in columns:
        op.drop_column("leave_master", "created_by")
