"""Fix broken merge head

Revision ID: cbb8a888cb3b
Revises: eaec9ea4abcd
Create Date: 2025-12-03 12:35:30.080702
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cbb8a888cb3b'
down_revision = 'eaec9ea4abcd'   # <-- Only ONE parent, no tuple
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
