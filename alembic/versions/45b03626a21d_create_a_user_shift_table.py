"""create a user shift table

Revision ID: 45b03626a21d
Revises: 23bbee4b6739
Create Date: 2025-10-29 17:43:55.911328
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '45b03626a21d'
down_revision: Union[str, Sequence[str], None] = '23bbee4b6739'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # --- Create attendances table if not exists ---
    if 'attendances' not in inspector.get_table_names():
        op.create_table(
            'attendances',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
            sa.Column('punch_id', sa.String(100), nullable=False),
            sa.Column('first_punch', sa.DateTime, nullable=True),
            sa.Column('last_punch', sa.DateTime, nullable=True),
            sa.Column('shift_start', sa.DateTime, nullable=True),
            sa.Column('shift_end', sa.DateTime, nullable=True),
            sa.Column('latitude', sa.Float, nullable=True),
            sa.Column('longitude', sa.Float, nullable=True),
            sa.Column('status', sa.String(50), nullable=True),
            sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=True),
            sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=True)
        )
        if 'ix_attendances_id' not in [idx['name'] for idx in inspector.get_indexes('attendances')]:
            op.create_index(op.f('ix_attendances_id'), 'attendances', ['id'], unique=False)

    # --- Create shift_change_requests table if not exists ---
    if 'shift_change_requests' not in inspector.get_table_names():
        op.create_table(
            'shift_change_requests',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
            sa.Column('old_shift_id', sa.Integer, sa.ForeignKey('shifts.id'), nullable=True),
            sa.Column('new_shift_id', sa.Integer, sa.ForeignKey('shifts.id'), nullable=False),
            sa.Column('request_date', sa.Date, nullable=False),
            sa.Column('reason', sa.String(255), nullable=True),
            sa.Column('status', sa.String(20), nullable=True)
        )
        if 'ix_shift_change_requests_id' not in [idx['name'] for idx in inspector.get_indexes('shift_change_requests')]:
            op.create_index(op.f('ix_shift_change_requests_id'), 'shift_change_requests', ['id'], unique=False)

    # --- Alter existing tables safely ---
    # candidate_documents
    existing_cols = [c['name'] for c in inspector.get_columns('candidate_documents')]
    if 'document_type' in existing_cols:
        op.alter_column('candidate_documents', 'document_type', existing_type=mysql.VARCHAR(length=50),
                        type_=sa.String(length=100), existing_nullable=False)
    if 'document_url' in existing_cols:
        op.alter_column('candidate_documents', 'document_url', existing_type=mysql.VARCHAR(length=500),
                        type_=sa.String(length=255), existing_nullable=False)

    # candidates
    existing_cols = [c['name'] for c in inspector.get_columns('candidates')]
    if 'last_name' in existing_cols:
        op.alter_column('candidates', 'last_name', existing_type=mysql.VARCHAR(length=100), nullable=False)
    if 'phone_number' in existing_cols:
        op.alter_column('candidates', 'phone_number', existing_type=mysql.VARCHAR(length=20), nullable=False)
    if 'resume_url' in existing_cols:
        op.alter_column('candidates', 'resume_url', existing_type=mysql.VARCHAR(length=500),
                        type_=sa.String(length=255), existing_nullable=True)
    if 'ix_candidates_id' not in [idx['name'] for idx in inspector.get_indexes('candidates')]:
        op.create_index(op.f('ix_candidates_id'), 'candidates', ['id'], unique=False)
    existing_constraints = [c['name'] for c in inspector.get_unique_constraints('candidates')]
    if 'email' not in existing_constraints:
        op.create_unique_constraint(None, 'candidates', ['email'])

    # job_postings
    existing_cols = [c['name'] for c in inspector.get_columns('job_postings')]
    if 'role_id' in existing_cols:
        op.alter_column('job_postings', 'role_id', existing_type=mysql.INTEGER(), nullable=True)
    if 'number_of_positions' in existing_cols:
        op.alter_column('job_postings', 'number_of_positions', existing_type=mysql.INTEGER(), nullable=True)
    if 'employment_type' in existing_cols:
        op.alter_column('job_postings', 'employment_type', existing_type=mysql.VARCHAR(length=50), nullable=True)
    if 'location' in existing_cols:
        op.alter_column('job_postings', 'location', existing_type=mysql.VARCHAR(length=150),
                        type_=sa.String(length=100), nullable=True)
    if 'salary' in existing_cols:
        op.alter_column('job_postings', 'salary', existing_type=mysql.FLOAT(), type_=sa.Integer(), existing_nullable=True)
    if 'posting_date' in existing_cols:
        op.alter_column('job_postings', 'posting_date', existing_type=sa.DATE(), nullable=True)
    if 'closing_date' in existing_cols:
        op.alter_column('job_postings', 'closing_date', existing_type=sa.DATE(), nullable=True)

    # drop old foreign keys safely
    try:
        op.drop_constraint(op.f('job_postings_ibfk_2'), 'job_postings', type_='foreignkey')
    except Exception:
        pass
    try:
        op.drop_constraint(op.f('job_postings_ibfk_1'), 'job_postings', type_='foreignkey')
    except Exception:
        pass
    op.create_foreign_key(None, 'job_postings', 'roles', ['role_id'], ['id'])

    # job_roles
    existing_cols = [c['name'] for c in inspector.get_columns('job_roles')]
    if 'required_skills' in existing_cols:
        op.alter_column('job_roles', 'required_skills', existing_type=mysql.TEXT(),
                        type_=sa.String(length=255), existing_nullable=True)
    if 'ix_job_roles_id' not in [idx['name'] for idx in inspector.get_indexes('job_roles')]:
        op.create_index(op.f('ix_job_roles_id'), 'job_roles', ['id'], unique=False)

    # leave_master
    leave_columns = [c['name'] for c in inspector.get_columns('leave_master')]
    if 'holiday' in leave_columns:
        op.alter_column('leave_master', 'holiday', existing_type=mysql.TINYINT(display_width=1),
                        type_=sa.String(length=100), nullable=False)
    if 'description' in leave_columns:
        op.alter_column('leave_master', 'description', existing_type=mysql.TEXT(),
                        type_=sa.String(length=255), existing_nullable=True)
    if 'user_id' in leave_columns:
        op.alter_column('leave_master', 'user_id', existing_type=mysql.INTEGER(), nullable=False)
    if 'leave_type' in leave_columns:
        op.alter_column('leave_master', 'leave_type', existing_type=mysql.ENUM(
            'CASUAL', 'SICK', 'EARNED', 'MATERNITY', 'BEREAVEMENT', 'STUDY',
            'SPECIAL', 'UNPAID', 'PUBLIC_HOLIDAY', 'COMP_OFF'),
            type_=sa.String(length=50), existing_nullable=False)
    if 'start_date' in leave_columns:
        op.alter_column('leave_master', 'start_date', existing_type=sa.DATE(), nullable=True)
    if 'end_date' in leave_columns:
        op.alter_column('leave_master', 'end_date', existing_type=sa.DATE(), nullable=True)

    # shifts
    shifts_cols = [c['name'] for c in inspector.get_columns('shifts')]
    if 'start_time' in shifts_cols:
        op.alter_column('shifts', 'start_time', existing_type=mysql.TIME(), type_=sa.String(length=10),
                        existing_nullable=False)
    if 'end_time' in shifts_cols:
        op.alter_column('shifts', 'end_time', existing_type=mysql.TIME(), type_=sa.String(length=10),
                        existing_nullable=False)
    if 'shift_code' in shifts_cols:
        op.alter_column('shifts', 'shift_code', existing_type=mysql.VARCHAR(length=50), type_=sa.String(length=20),
                        existing_nullable=False)

    # users
    users_cols = [c['name'] for c in inspector.get_columns('users')]
    if 'first_name' in users_cols:
        op.alter_column('users', 'first_name', existing_type=mysql.VARCHAR(length=100),
                        type_=sa.String(length=50), existing_nullable=False)
    if 'last_name' in users_cols:
        op.alter_column('users', 'last_name', existing_type=mysql.VARCHAR(length=100), type_=sa.String(length=50),
                        nullable=True)
    if 'hashed_password' in users_cols:
        op.alter_column('users', 'hashed_password', existing_type=mysql.VARCHAR(length=200),
                        type_=sa.String(length=255), existing_nullable=False)
    if 'role_id' in users_cols:
        op.alter_column('users', 'role_id', existing_type=mysql.INTEGER(), nullable=False)
    if 'date_of_birth' in users_cols:
        op.alter_column('users', 'date_of_birth', existing_type=mysql.DATETIME(), type_=sa.Date(),
                        existing_nullable=True)
    if 'joining_date' in users_cols:
        op.alter_column('users', 'joining_date', existing_type=mysql.DATETIME(), type_=sa.Date(),
                        existing_nullable=True)
    if 'relieving_date' in users_cols:
        op.alter_column('users', 'relieving_date', existing_type=mysql.DATETIME(), type_=sa.Date(),
                        existing_nullable=True)
    if 'address' in users_cols:
        op.alter_column('users', 'address', existing_type=mysql.VARCHAR(length=500),
                        type_=sa.String(length=255), existing_nullable=True)
    if 'biometric_id' in users_cols:
        op.alter_column('users', 'biometric_id', existing_type=mysql.VARCHAR(length=255),
                        type_=sa.String(length=50), existing_nullable=True)

    try:
        op.drop_index(op.f('biometric_id'), table_name='users')
    except Exception:
        pass
    try:
        op.drop_constraint(op.f('users_ibfk_2'), 'users', type_='foreignkey')
    except Exception:
        pass
    try:
        op.drop_constraint(op.f('fk_users_branch_id'), 'users', type_='foreignkey')
    except Exception:
        pass
    op.create_foreign_key(None, 'users', 'organizations', ['organization_id'], ['id'])
    op.create_foreign_key(None, 'users', 'branches', ['branch_id'], ['id'])

    # workflows
    workflows_cols = [c['name'] for c in inspector.get_columns('workflows')]
    if 'approval_status' in workflows_cols:
        op.alter_column('workflows', 'approval_status', existing_type=mysql.ENUM('Pending', 'Approved', 'Rejected'),
                        type_=sa.String(length=50), existing_nullable=True)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # Drop tables only if exist
    if 'shift_change_requests' in inspector.get_table_names():
        op.drop_index(op.f('ix_shift_change_requests_id'), table_name='shift_change_requests')
        op.drop_table('shift_change_requests')

    if 'attendances' in inspector.get_table_names():
        op.drop_index(op.f('ix_attendances_id'), table_name='attendances')
        op.drop_table('attendances')
