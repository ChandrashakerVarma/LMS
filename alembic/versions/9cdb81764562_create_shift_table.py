# """create shift table

# # Revision ID: 9cdb81764562
# Revises: b7d257e37d55
# Create Date: 2025-09-24 17:56:57.930745

# """
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '9cdb81764562'
down_revision: Union[str, Sequence[str], None] = 'b7d257e37d55'
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
    # Alter 'photo' column only if it exists
    if column_exists('users', 'photo'):
        op.alter_column(
            'users',
            'photo',
            type_=sa.LargeBinary(),   # BYTEA for PostgreSQL
            existing_type=sa.String(length=200),
            existing_nullable=True
        )
    
    # Create 'shift' table
    op.create_table(
        'shift',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('shift_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('shift_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop 'shift' table
    op.drop_table('shift')
    
    # Revert 'photo' column back to VARCHAR if it exists
    if column_exists('users', 'photo'):
        op.alter_column(
            'users',
            'photo',
            type_=sa.String(length=200),
            existing_type=sa.LargeBinary(),
            existing_nullable=True
        )
