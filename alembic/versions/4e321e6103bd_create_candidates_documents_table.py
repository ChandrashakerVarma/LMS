"""create candidates documents table

Revision ID: 4e321e6103bd
Revises: 49eddf5c0ff3
Create Date: 2025-10-29 12:21:01.736347
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '4e321e6103bd'
down_revision: Union[str, Sequence[str], None] = '49eddf5c0ff3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema safely."""
    conn = op.get_bind()
    inspector = inspect(conn)

    # ✅ Drop user_shifts safely only if it exists
    if 'user_shifts' in inspector.get_table_names():
        indexes = [idx['name'] for idx in inspector.get_indexes('user_shifts')]
        if 'ix_user_shifts_id' in indexes:
            op.drop_index('ix_user_shifts_id', table_name='user_shifts')
        op.drop_table('user_shifts')

    # ✅ Candidate documents
    if 'candidate_documents' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('candidate_documents')]
        if 'document_type' in cols:
            op.alter_column(
                'candidate_documents', 'document_type',
                existing_type=mysql.VARCHAR(length=50),
                type_=sa.String(length=100),
                existing_nullable=False
            )
        if 'document_url' in cols:
            op.alter_column(
                'candidate_documents', 'document_url',
                existing_type=mysql.VARCHAR(length=500),
                type_=sa.String(length=255),
                existing_nullable=False
            )

    # ✅ Candidates table
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

    # ⚠️ Removed duplicate index on primary key 'id'
    # Primary key already creates an index automatically
    # op.create_index(op.f('ix_candidates_id'), 'candidates', ['id'], unique=False)

    op.create_unique_constraint(None, 'candidates', ['email'])

    # ✅ Job postings updates
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

    # ✅ Safe foreign key cleanup
    fks = [fk['name'] for fk in inspector.get_foreign_keys('job_postings')]
    if 'job_postings_ibfk_1' in fks:
        op.drop_constraint('job_postings_ibfk_1', 'job_postings', type_='foreignkey')
    if 'job_postings_ibfk_2' in fks:
        op.drop_constraint('job_postings_ibfk_2', 'job_postings', type_='foreignkey')
    op.create_foreign_key(None, 'job_postings', 'roles', ['role_id'], ['id'])

    # ✅ Job roles
    op.alter_column('job_roles', 'required_skills',
                    existing_type=mysql.TEXT(),
                    type_=sa.String(length=255),
                    existing_nullable=True)

    # ⚠️ Removed duplicate index creation on primary key
    # op.create_index(op.f('ix_job_roles_id'), 'job_roles', ['id'], unique=False)

    # ✅ Leave master
    cols = [c['name'] for c in inspector.get_columns('leave_master')]
    if 'name' not in cols:
        op.add_column('leave_master', sa.Column('name', sa.String(length=100), nullable=True))
    if 'status' not in cols:
        op.add_column('leave_master', sa.Column('status', sa.Boolean(), nullable=True))
    if 'date' not in cols:
        op.add_column('leave_master', sa.Column('date', sa.Date(), nullable=True))
    if 'year' not in cols:
        op.add_column('leave_master', sa.Column('year', sa.Integer(), nullable=True))
    for col in ['start_date', 'end_date', 'leave_type']:
        if col in cols:
            op.drop_column('leave_master', col)

    # ✅ Quiz checkpoints
    fks = [fk['name'] for fk in inspector.get_foreign_keys('quiz_checkpoints')]
    if 'quiz_checkpoints_ibfk_2' in fks:
        op.drop_constraint('quiz_checkpoints_ibfk_2', 'quiz_checkpoints', type_='foreignkey')
    cols = [c['name'] for c in inspector.get_columns('quiz_checkpoints')]
    if 'course_id' in cols:
        op.drop_column('quiz_checkpoints', 'course_id')

    # ✅ Shifts table
    cols = [c['name'] for c in inspector.get_columns('shifts')]
    if 'name' not in cols:
        op.add_column('shifts', sa.Column('name', sa.String(length=100), nullable=False))
    if 'description' not in cols:
        op.add_column('shifts', sa.Column('description', sa.String(length=255), nullable=True))
    if 'shift_name' not in cols:
        op.add_column('shifts', sa.Column('shift_name', sa.String(length=100), nullable=False))
    op.create_unique_constraint(None, 'shifts', ['name'])
    if 'is_rotational' in cols:
        op.drop_column('shifts', 'is_rotational')

    # ✅ Users table
    cols = [c['name'] for c in inspector.get_columns('users')]
    if 'name' not in cols:
        op.add_column('users', sa.Column('name', sa.String(length=100), nullable=False))
    for col in ['last_name', 'first_name', 'biometric_id']:
        if col in cols:
            op.drop_column('users', col)

    # ✅ Workflows
    op.alter_column('workflows', 'approval_status',
                    existing_type=mysql.ENUM('Pending', 'Approved', 'Rejected'),
                    type_=sa.String(length=50),
                    existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema safely."""
    op.execute("DELETE FROM alembic_version WHERE version_num = '4e321e6103bd'")
