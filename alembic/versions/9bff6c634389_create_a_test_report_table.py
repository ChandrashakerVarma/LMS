"""create test_reports table

Revision ID: 9bff6c634389
Revises: 3877ab94139f
Create Date: 2025-12-16 11:04:15.655244
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9bff6c634389'
down_revision = '3877ab94139f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema: create test_reports table."""
    op.create_table(
        'test_reports',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('module_name', sa.String(length=255), nullable=False),
        sa.Column('total_tests', sa.Integer, nullable=False),
        sa.Column('passed', sa.Integer, nullable=False),
        sa.Column('failed', sa.Integer, nullable=False),
        sa.Column('failures', sa.Text, nullable=True),  # JSON stored as string for MySQL
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )

def downgrade() -> None:
    """Downgrade schema: drop test_reports table."""
    op.drop_table('test_reports')
