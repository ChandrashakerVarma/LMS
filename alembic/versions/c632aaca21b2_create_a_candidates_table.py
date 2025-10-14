"""create a candidates table

Revision ID: c632aaca21b2
Revises: f83a205910c7
Create Date: 2025-10-10 13:37:02.090161
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'c632aaca21b2'
down_revision: Union[str, Sequence[str], None] = 'f83a205910c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = inspect(conn)

    # Check existing columns in job_postings
    columns = [col['name'] for col in inspector.get_columns('job_postings')]

    if 'created_by_id' not in columns:
        op.add_column('job_postings', sa.Column('created_by_id', sa.Integer(), nullable=False))
        op.create_foreign_key(None, 'job_postings', 'users', ['created_by_id'], ['id'])
    else:
        print("⚠️ Column 'created_by_id' already exists — skipping addition.")


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    inspector = inspect(conn)

    # Check existing columns in job_postings
    columns = [col['name'] for col in inspector.get_columns('job_postings')]

    if 'created_by_id' in columns:
        op.drop_constraint(None, 'job_postings', type_='foreignkey')
        op.drop_column('job_postings', 'created_by_id')
    else:
        print("⚠️ Column 'created_by_id' does not exist — skipping drop.")
