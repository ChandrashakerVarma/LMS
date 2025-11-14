"""create attendance and shift_change_requests tables safely

Revision ID: d0b9370aa848
Revises: 8de67cf8163e
Create Date: 2025-10-29 17:16:08.454994
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'd0b9370aa848'
down_revision: Union[str, Sequence[str], None] = '8de67cf8163e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    conn = op.get_bind()
    inspector = inspect(conn)

    # --- Create attendances table if it doesn't exist ---
    if 'attendances' not in inspector.get_table_names():
        op.create_table(
            'attendances',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('punch_id', sa.String(100), nullable=False),
            sa.Column('first_punch', sa.DateTime(), nullable=True),
            sa.Column('last_punch', sa.DateTime(), nullable=True),
            sa.Column('shift_start', sa.DateTime(), nullable=True),
            sa.Column('shift_end', sa.DateTime(), nullable=True),
            sa.Column('latitude', sa.Float(), nullable=True),
            sa.Column('longitude', sa.Float(), nullable=True),
            sa.Column('status', sa.String(50), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        )
        op.create_index(op.f('ix_attendances_id'), 'attendances', ['id'], unique=False)

    # --- Create shift_change_requests table if it doesn't exist ---
    if 'shift_change_requests' not in inspector.get_table_names():
        op.create_table(
            'shift_change_requests',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('old_shift_id', sa.Integer(), sa.ForeignKey('shifts.id'), nullable=True),
            sa.Column('new_shift_id', sa.Integer(), sa.ForeignKey('shifts.id'), nullable=False),
            sa.Column('request_date', sa.Date(), nullable=False),
            sa.Column('reason', sa.String(255), nullable=True),
            sa.Column('status', sa.String(20), nullable=True),
        )
        op.create_index(op.f('ix_shift_change_requests_id'), 'shift_change_requests', ['id'], unique=False)

    # --- Alter candidate_documents table ---
    op.alter_column('candidate_documents', 'document_type',
               existing_type=mysql.VARCHAR(length=50),
               type_=sa.String(length=100),
               existing_nullable=False)
    op.alter_column('candidate_documents', 'document_url',
               existing_type=mysql.VARCHAR(length=500),
               type_=sa.String(length=255),
               existing_nullable=False)

    # --- Alter candidates table ---
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
    op.create_index(op.f('ix_candidates_id'), 'candidates', ['id'], unique=False)
    op.create_unique_constraint(None, 'candidates', ['email'])

    # --- Alter job_postings table ---
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
    op.drop_constraint(op.f('job_postings_ibfk_1'), 'job_postings', type_='foreignkey')
    op.drop_constraint(op.f('job_postings_ibfk_2'), 'job_postings', type_='foreignkey')
    op.create_foreign_key(None, 'job_postings', 'roles', ['role_id'], ['id'])

    # --- Alter job_roles table ---
    op.alter_column('job_roles', 'required_skills',
               existing_type=mysql.TEXT(),
               type_=sa.String(length=255),
               existing_nullable=True)
    op.create_index(op.f('ix_job_roles_id'), 'job_roles', ['id'], unique=False)

    # --- Alter leave_master table ---
    op.alter_column('leave_master', 'holiday',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.String(length=100),
               nullable=False)
    op.alter_column('leave_master', 'description',
               existing_type=mysql.TEXT(),
               type_=sa.String(length=255),
               existing_nullable=True)
    op.alter_column('leave_master', 'user_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.alter_column('leave_master', 'leave_type',
               existing_type=mysql.ENUM('CASUAL', 'SICK', 'EARNED', 'MATERNITY', 'BEREAVEMENT', 'STUDY', 'SPECIAL', 'UNPAID', 'PUBLIC_HOLIDAY', 'COMP_OFF'),
               type_=sa.String(length=50),
               existing_nullable=False)
    op.alter_column('leave_master', 'start_date',
               existing_type=sa.DATE(),
               nullable=True)
    op.alter_column('leave_master', 'end_date',
               existing_type=sa.DATE(),
               nullable=True)

    # --- Alter quiz_checkpoints table ---
    op.drop_constraint(op.f('quiz_checkpoints_ibfk_2'), 'quiz_checkpoints', type_='foreignkey')
    op.drop_column('quiz_checkpoints', 'course_id')

    # --- Alter shifts table ---
    op.alter_column('shifts', 'start_time',
               existing_type=mysql.TIME(),
               type_=sa.String(length=10),
               existing_nullable=False)
    op.alter_column('shifts', 'end_time',
               existing_type=mysql.TIME(),
               type_=sa.String(length=10),
               existing_nullable=False)
    op.alter_column('shifts', 'shift_code',
               existing_type=mysql.VARCHAR(length=50),
               type_=sa.String(length=20),
               existing_nullable=False)

    # --- Alter users table ---
    op.add_column('users', sa.Column('name', sa.String(length=100), nullable=False))
    op.drop_index(op.f('biometric_id'), table_name='users')
    op.drop_column('users', 'biometric_id')
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')

    # --- Alter workflows table ---
    op.alter_column('workflows', 'approval_status',
               existing_type=mysql.ENUM('Pending', 'Approved', 'Rejected'),
               type_=sa.String(length=50),
               existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    inspector = inspect(conn)

    if 'shift_change_requests' in inspector.get_table_names():
        op.drop_index(op.f('ix_shift_change_requests_id'), table_name='shift_change_requests')
        op.drop_table('shift_change_requests')

    if 'attendances' in inspector.get_table_names():
        op.drop_index(op.f('ix_attendances_id'), table_name='attendances')
        op.drop_table('attendances')

    # Remaining downgrade commands from your original migration can follow here...
