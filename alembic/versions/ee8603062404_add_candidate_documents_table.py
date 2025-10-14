"""Add candidate_documents table

Revision ID: ee8603062404
Revises: c632aaca21b2
Create Date: 2025-10-13 13:26:09.027057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee8603062404'
down_revision: Union[str, Sequence[str], None] = 'c632aaca21b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'candidate_documents',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('candidate_id', sa.Integer, sa.ForeignKey('candidates.id'), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('document_url', sa.String(500), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('candidate_documents')
