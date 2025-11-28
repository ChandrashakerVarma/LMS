"""srilaxmi changes

Revision ID: 7de48520aeb8
Revises: 1aac06f04dc2
Create Date: 2025-11-27 15:09:28.188002
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect


# revision identifiers
revision: str = '7de48520aeb8'
down_revision: Union[str, Sequence[str], None] = '1aac06f04dc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # ========== 1) CREATE job_descriptions table safely ==========
    if 'job_descriptions' not in inspector.get_table_names():
        op.create_table(
            'job_descriptions',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('description', sa.String(1000)),
            sa.Column('required_skills', sa.String(1000)),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(timezone=True)),
            sa.Column('created_by', sa.String(100)),
            sa.Column('modified_by', sa.String(100)),
        )
        op.create_index(op.f('ix_job_descriptions_id'), 'job_descriptions', ['id'])

    # ========== 2) DROP workflows if exists ==========
    if 'workflows' in inspector.get_table_names():
        op.drop_table('workflows')

    # ========== 3) Drop FK from job_postings -> job_roles before deleting table ==========
    fk_names = [fk['name'] for fk in inspector.get_foreign_keys('job_postings')]
    for fk in fk_names:
        op.drop_constraint(fk, 'job_postings', type_='foreignkey')

    # ========== 4) DROP job_roles safely ==========
    if 'job_roles' in inspector.get_table_names():
        op.drop_table('job_roles')

    # ========== 5) Add new columns to job_postings only if missing ==========
    existing_cols = [c['name'] for c in inspector.get_columns('job_postings')]

    if 'job_description_id' not in existing_cols:
        op.add_column('job_postings', sa.Column('job_description_id', sa.Integer(), nullable=False))

    if 'created_by_id' not in existing_cols:
        op.add_column('job_postings', sa.Column('created_by_id', sa.Integer(), nullable=False))

    if 'created_by_name' not in existing_cols:
        op.add_column('job_postings', sa.Column('created_by_name', sa.String(100)))

    if 'approval_status' not in existing_cols:
        op.add_column('job_postings', sa.Column(
            'approval_status',
            sa.Enum('pending', 'accepted', 'rejected', name='approvalstatus'),
            nullable=False
        ))

    # ========== 6) Create new relations ==========
    op.create_foreign_key('fk_job_postings_created_by', 'job_postings', 'users', ['created_by_id'], ['id'])
    op.create_foreign_key('fk_job_postings_description', 'job_postings', 'job_descriptions', ['job_description_id'], ['id'])

    # ========== 7) DROP old columns if exist ==========
    existing_cols = [c['name'] for c in inspector.get_columns('job_postings')]

    if 'created_by' in existing_cols:
        op.drop_column('job_postings', 'created_by')

    if 'job_role_id' in existing_cols:
        op.drop_column('job_postings', 'job_role_id')

    # ========== 8) Update shifts.created_by datatype ==========
    op.alter_column(
        'shifts', 'created_by',
        existing_type=mysql.VARCHAR(length=100),
        type_=sa.Integer(),
        nullable=False
    )
    op.create_foreign_key('fk_shifts_created_by', 'shifts', 'users', ['created_by'], ['id'])

    # ========== 9) Add department_id to users ==========
    user_cols = [c['name'] for c in inspector.get_columns('users')]
    if 'department_id' not in user_cols:
        op.add_column('users', sa.Column('department_id', sa.Integer()))
        op.create_foreign_key('fk_user_department', 'users', 'departments', ['department_id'], ['id'])



def downgrade() -> None:

    op.drop_constraint('fk_user_department', 'users', type_='foreignkey')
    op.drop_column('users', 'department_id')

    op.drop_constraint('fk_shifts_created_by', 'shifts', type_='foreignkey')
    op.alter_column('shifts', 'created_by', existing_type=sa.Integer(), type_=mysql.VARCHAR(length=100), nullable=True)

    op.drop_constraint('fk_job_postings_description', 'job_postings', type_='foreignkey')
    op.drop_constraint('fk_job_postings_created_by', 'job_postings', type_='foreignkey')
    op.drop_column('job_postings', 'approval_status')
    op.drop_column('job_postings', 'created_by_name')
    op.drop_column('job_postings', 'created_by_id')
    op.drop_column('job_postings', 'job_description_id')

    # Restore job_roles
    op.create_table(
        'job_roles',
        sa.Column('id', mysql.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('title', mysql.VARCHAR(255), nullable=False),
        sa.Column('description', mysql.VARCHAR(1000)),
        sa.Column('required_skills', mysql.VARCHAR(1000)),
        sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('(now())')),
        sa.Column('updated_at', mysql.DATETIME()),
        sa.Column('created_by', mysql.VARCHAR(100)),
        sa.Column('modified_by', mysql.VARCHAR(100)),
        mysql_engine='InnoDB', mysql_default_charset='utf8mb4', mysql_collate='utf8mb4_0900_ai_ci'
    )
    op.create_index(op.f('ix_job_roles_id'), 'job_roles', ['id'])

    # Restore workflows
    op.create_table(
        'workflows',
        sa.Column('id', mysql.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('posting_id', mysql.INTEGER()),
        sa.Column('approval_status', mysql.ENUM('pending', 'accepted', 'rejected')),
        sa.ForeignKeyConstraint(['posting_id'], ['job_postings.id']),
        mysql_engine='InnoDB', mysql_default_charset='utf8mb4', mysql_collate='utf8mb4_0900_ai_ci'
    )

    op.drop_index(op.f('ix_job_descriptions_id'), table_name='job_descriptions')
    op.drop_table('job_descriptions')
