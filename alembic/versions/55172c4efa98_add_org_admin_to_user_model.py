"""safe migration - avoid duplicate is_org_admin column

Revision ID: 55172c4efa98
Revises: 494a05653bbb
Create Date: 2025-12-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = '55172c4efa98'
down_revision = '494a05653bbb'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns("users")]

    # SAFE → Add only if missing  
    if "is_org_admin" not in columns:
        op.add_column("users", sa.Column("is_org_admin", sa.Boolean(), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns("users")]

    # SAFE → Drop only if exists  
    if "is_org_admin" in columns:
        op.drop_column("users", "is_org_admin")
