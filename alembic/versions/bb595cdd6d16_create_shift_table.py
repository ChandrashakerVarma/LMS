"""create shift table

Revision ID: bb595cdd6d16
Revises: 9cdb81764562
Create Date: 2025-09-24 22:13:43.885572

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'bb595cdd6d16'
down_revision: Union[str, Sequence[str], None] = '9cdb81764562'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in the given table."""
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    """Upgrade schema."""
    # Drop 'photo' column only if it exists
    if column_exists('users', 'photo'):
        op.drop_column('users', 'photo')


def downgrade() -> None:
    """Downgrade schema."""
    # Add 'photo' column back if it does not exist
    if not column_exists('users', 'photo'):
        op.add_column('users', sa.Column('photo', sa.LargeBinary(), nullable=True))
