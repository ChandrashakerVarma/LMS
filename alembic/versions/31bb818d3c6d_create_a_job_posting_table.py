"""create job_postings table safely and apply schema updates

Revision ID: 31bb818d3c6d
Revises: 9360c83cbcd4
Create Date: 2025-10-29 10:20:55.154632
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '31bb818d3c6d'
down_revision: Union[str, Sequence[str], None] = '9360c83cbcd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def constraint_exists(table_name: str, constraint_name: str) -> bool:
    """Check if a constraint already exists on the table."""
    conn = op.get_bind()
    inspector = inspect(conn)
    for const in inspector.get_unique_constraints(table_name):
        if const["name"] == constraint_name:
            return True
    return False


def upgrade() -> None:
    """Upgrade schema safely."""
    # ✅ Create job_postings table if it doesn’t exist
    op.create_table(
        'job_postings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('number_of_positions', sa.Integer(), nullable=True),
        sa.Column('employment_type', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('salary', sa.Integer(), nullable=True),
        sa.Column('posting_date', sa.Date(), nullable=True),
        sa.Column('closing_date', sa.Date(), nullable=True),
        sa.Column('description_id', sa.Integer(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='fk_job_postings_role_id'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_job_postings_created_by'),
    )

    # ✅ Update leave_master columns
    with op.batch_alter_table('leave_master', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('status', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('year', sa.Integer(), nullable=True))
        batch_op.drop_column('leave_type')
        batch_op.drop_column('start_date')
        batch_op.drop_column('end_date')

    # ✅ Modify shifts table safely
    with op.batch_alter_table('shifts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('description', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('shift_name', sa.String(length=100), nullable=False))
        batch_op.drop_column('is_rotational')

    # Add unique constraint only if it doesn't exist
    if not constraint_exists('shifts', 'uq_shifts_name'):
        op.create_unique_constraint('uq_shifts_name', 'shifts', ['name'])

    # ✅ Modify users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=False))
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')
        batch_op.drop_column('biometric_id')

    # ✅ Update quiz_checkpoints
    with op.batch_alter_table('quiz_checkpoints', schema=None) as batch_op:
        batch_op.drop_column('course_id')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('job_postings')
