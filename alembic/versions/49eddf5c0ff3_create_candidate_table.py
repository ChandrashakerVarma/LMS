"""create candidate table

Revision ID: 49eddf5c0ff3
Revises: f29d20bc21fc
Create Date: 2025-10-29 12:13:30.325225
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '49eddf5c0ff3'
down_revision: Union[str, Sequence[str], None] = 'f29d20bc21fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = inspect(conn)

    # ✅ Create candidates table if not exists
    if 'candidates' not in inspector.get_table_names():
        op.create_table(
            'candidates',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('first_name', sa.String(100), nullable=False),
            sa.Column('last_name', sa.String(100), nullable=False),
            sa.Column('email', sa.String(200), nullable=False, unique=True),
            sa.Column('phone_number', sa.String(20), nullable=False),
            sa.Column('resume_url', sa.String(255), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        )

    # ✅ Drop candidate_documents safely
    if 'candidate_documents' in inspector.get_table_names():
        indexes = [idx['name'] for idx in inspector.get_indexes('candidate_documents')]
        if 'ix_candidate_documents_id' in indexes:
            op.drop_index('ix_candidate_documents_id', table_name='candidate_documents')
        op.drop_table('candidate_documents')

    # ✅ Drop user_shifts safely
    if 'user_shifts' in inspector.get_table_names():
        indexes = [idx['name'] for idx in inspector.get_indexes('user_shifts')]
        if 'ix_user_shifts_id' in indexes:
            op.drop_index('ix_user_shifts_id', table_name='user_shifts')
        op.drop_table('user_shifts')

    # ✅ Alter candidates table safely
    if 'candidates' in inspector.get_table_names():
        op.alter_column('candidates', 'last_name',
                        existing_type=mysql.VARCHAR(length=100),
                        nullable=False)
        op.alter_column('candidates', 'phone_number',
                        existing_type=mysql.VARCHAR(length=20),
                        nullable=False)
        op.alter_column('candidates', 'resume_url',
                        existing_type=mysql.VARCHAR(length=500),
                        type_=sa.String(length=255),
                        existing_nullable=True)

        indexes = [idx['name'] for idx in inspector.get_indexes('candidates')]
        if 'ix_candidates_id' not in indexes:
            op.create_index(op.f('ix_candidates_id'), 'candidates', ['id'], unique=False)

        constraints = [uc['column_names'] for uc in inspector.get_unique_constraints('candidates')]
        if ['email'] not in constraints:
            op.create_unique_constraint(None, 'candidates', ['email'])

    # ✅ job_postings table updates
    op.alter_column('job_postings', 'role_id',
                    existing_type=mysql.INTEGER(),
                    nullable=True)
    op.alter_column('job_postings', 'number_of_positions',
                    existing_type=mysql.INTEGER(),
                    nullable=True)
    op.alter_column('job_postings', 'employment_type',
                    existing_type=mysql.VARCHAR(length=50),
                    nullable=True)
    op.alter_column('job_postings', 'location',
                    existing_type=mysql.VARCHAR(length=150),
                    type_=sa.String(length=100),
                    nullable=True)
    op.alter_column('job_postings', 'salary',
                    existing_type=mysql.FLOAT(),
                    type_=sa.Integer(),
                    existing_nullable=True)
    op.alter_column('job_postings', 'posting_date',
                    existing_type=sa.DATE(),
                    nullable=True)
    op.alter_column('job_postings', 'closing_date',
                    existing_type=sa.DATE(),
                    nullable=True)
    op.alter_column('job_postings', 'description_id',
                    existing_type=mysql.INTEGER(),
                    nullable=True)
    op.alter_column('job_postings', 'created_by_id',
                    existing_type=mysql.INTEGER(),
                    nullable=True)

    fks = [fk['name'] for fk in inspector.get_foreign_keys('job_postings')]
    if 'job_postings_ibfk_1' in fks:
        op.drop_constraint('job_postings_ibfk_1', 'job_postings', type_='foreignkey')
    if 'job_postings_ibfk_2' in fks:
        op.drop_constraint('job_postings_ibfk_2', 'job_postings', type_='foreignkey')
    op.create_foreign_key(None, 'job_postings', 'roles', ['role_id'], ['id'])

    # ✅ job_roles table fix (prevent duplicate index)
    op.alter_column('job_roles', 'required_skills',
                    existing_type=mysql.TEXT(),
                    type_=sa.String(length=255),
                    existing_nullable=True)

    job_role_indexes = [idx['name'] for idx in inspector.get_indexes('job_roles')]
    if 'ix_job_roles_id' not in job_role_indexes:
        op.create_index(op.f('ix_job_roles_id'), 'job_roles', ['id'], unique=False)

    # ✅ leave_master updates (safe version)
    leave_columns = [c['name'] for c in inspector.get_columns('leave_master')]

    if 'name' not in leave_columns:
        op.add_column('leave_master', sa.Column('name', sa.String(length=100), nullable=True))
    if 'status' not in leave_columns:
        op.add_column('leave_master', sa.Column('status', sa.Boolean(), nullable=True))
    if 'date' not in leave_columns:
        op.add_column('leave_master', sa.Column('date', sa.Date(), nullable=True))
    if 'year' not in leave_columns:
        op.add_column('leave_master', sa.Column('year', sa.Integer(), nullable=True))

    if 'end_date' in leave_columns:
        op.drop_column('leave_master', 'end_date')
    if 'leave_type' in leave_columns:
        op.drop_column('leave_master', 'leave_type')
    if 'start_date' in leave_columns:
        op.drop_column('leave_master', 'start_date')

    # ✅ quiz_checkpoints cleanup
    fks = [fk['name'] for fk in inspector.get_foreign_keys('quiz_checkpoints')]
    if 'quiz_checkpoints_ibfk_2' in fks:
        op.drop_constraint('quiz_checkpoints_ibfk_2', 'quiz_checkpoints', type_='foreignkey')
    cols = [c['name'] for c in inspector.get_columns('quiz_checkpoints')]
    if 'course_id' in cols:
        op.drop_column('quiz_checkpoints', 'course_id')

    # ✅ shifts table (safe)
    shift_columns = [c['name'] for c in inspector.get_columns('shifts')]
    if 'name' not in shift_columns:
        op.add_column('shifts', sa.Column('name', sa.String(length=100), nullable=False))
    if 'description' not in shift_columns:
        op.add_column('shifts', sa.Column('description', sa.String(length=255), nullable=True))
    if 'shift_name' not in shift_columns:
        op.add_column('shifts', sa.Column('shift_name', sa.String(length=100), nullable=False))
    shift_constraints = [uc['column_names'] for uc in inspector.get_unique_constraints('shifts')]
    if ['name'] not in shift_constraints:
        op.create_unique_constraint(None, 'shifts', ['name'])
    if 'is_rotational' in shift_columns:
        op.drop_column('shifts', 'is_rotational')

    # ✅ users table (safe)
    user_columns = [c['name'] for c in inspector.get_columns('users')]
    if 'name' not in user_columns:
        op.add_column('users', sa.Column('name', sa.String(length=100), nullable=False))
    indexes = [idx['name'] for idx in inspector.get_indexes('users')]
    if 'biometric_id' in indexes:
        op.drop_index('biometric_id', table_name='users')
    for col in ['last_name', 'biometric_id', 'first_name']:
        if col in user_columns:
            op.drop_column('users', col)

    # ✅ workflows table
    op.alter_column('workflows', 'approval_status',
                    existing_type=mysql.ENUM('Pending', 'Approved', 'Rejected'),
                    type_=sa.String(length=50),
                    existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    pass
