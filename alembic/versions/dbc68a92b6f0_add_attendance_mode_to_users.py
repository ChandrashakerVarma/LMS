"""add attendance_mode to users

Revision ID: dbc68a92b6f0
Revises: 502da61cf3c9
Create Date: 2025-12-04 13:33:00.088689
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "dbc68a92b6f0"
down_revision: Union[str, Sequence[str], None] = "502da61cf3c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [col["name"] for col in inspector.get_columns("users")]

    # Only add if it doesn't exist
    if "attendance_mode" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "attendance_mode",
                sa.String(20),
                nullable=False,
                server_default="BRANCH",
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [col["name"] for col in inspector.get_columns("users")]

    if "attendance_mode" in columns:
        op.drop_column("users", "attendance_mode")
