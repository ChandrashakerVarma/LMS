"""fix created_by field

Revision ID: a51406b58f4a
Revises: 7778a910a27e
Create Date: 2025-11-29 14:02:04.449160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'a51406b58f4a'
down_revision: Union[str, Sequence[str], None] = '7778a910a27e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    # Fix candidate_documents
    op.alter_column('candidate_documents', 'candidate_id',
               existing_type=mysql.INTEGER(),
               nullable=True)

    op.alter_column('candidate_documents', 'document_type',
               existing_type=mysql.VARCHAR(length=100),
               type_=sa.String(length=255),
               existing_nullable=False)

    op.alter_column('candidate_documents', 'document_url',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.String(length=500),
               existing_nullable=False)

    # job_postings: add created_by column if missing
    job_posting_cols = [col["name"] for col in inspector.get_columns("job_postings")]
    if "created_by" not in job_posting_cols:
        op.add_column('job_postings', sa.Column('created_by', sa.String(length=100), nullable=True))

    # Drop old FK and columns if present
    constraints = inspector.get_foreign_keys('job_postings')
    for fk in constraints:
        if fk['constrained_columns'] == ['created_by_id']:
            op.drop_constraint(fk['name'], 'job_postings', type_='foreignkey')

    if "created_by_name" in job_posting_cols:
        op.drop_column('job_postings', 'created_by_name')

    if "created_by_id" in job_posting_cols:
        op.drop_column('job_postings', 'created_by_id')

    # organizations: DO NOT ADD organization_logo (already exists)
    org_cols = [col["name"] for col in inspector.get_columns("organizations")]

    # If old column exists, drop it
    if "Organization_logo" in org_cols:
        op.drop_column('organizations', 'Organization_logo')

    # Do NOT re-add organization_logo — it already exists!


def downgrade() -> None:
    """Downgrade schema."""
    # Add back removed organization column
    op.add_column('organizations', sa.Column('Organization_logo', mysql.VARCHAR(length=255), nullable=True))
    op.drop_column('organizations', 'organization_logo')

    # Restore job_posting fields
    op.add_column('job_postings', sa.Column('created_by_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('job_postings', sa.Column('created_by_name', mysql.VARCHAR(length=100), nullable=True))
    op.create_foreign_key(op.f('fk_job_postings_created_by'), 'job_postings', 'users', ['created_by_id'], ['id'])
    op.drop_column('job_postings', 'created_by')

    # Revert candidate_documents fields
    op.alter_column('candidate_documents', 'document_url',
               existing_type=sa.String(length=500),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=False)

    op.alter_column('candidate_documents', 'document_type',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=100),
               existing_nullable=False)

    op.alter_column('candidate_documents', 'candidate_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
