"""update job_postings audit fields

Revision ID: 4943ba5e7c95
Revises: 7b56a030a5c5
Create Date: 2025-11-20 16:50:50.020480
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4943ba5e7c95'
down_revision: Union[str, Sequence[str], None] = '7b56a030a5c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop the foreign key first
    with op.batch_alter_table('job_postings') as batch_op:
        batch_op.drop_constraint('job_postings_ibfk_1', type_='foreignkey')  # <-- drop FK
        batch_op.drop_column('created_by_id')  # now safe to drop

        # Add new audit fields
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('modified_by', sa.String(length=100), nullable=True))


def downgrade():
    # Revert changes
    with op.batch_alter_table('job_postings') as batch_op:
        batch_op.drop_column('modified_by')
        batch_op.drop_column('created_by')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')

        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('job_postings_ibfk_1', 'users', ['created_by_id'], ['id'])  # recreate FK
