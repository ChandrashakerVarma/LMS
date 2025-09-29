"""add category_id to courses

Revision ID: 7d54448aa394
Revises: bf71b3071930
Create Date: 2025-09-27 13:57:54.048413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d54448aa394'
down_revision: Union[str, Sequence[str], None] = 'bf71b3071930'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('courses', sa.Column('category_id', sa.Integer, nullable=True))
    op.create_foreign_key(
        'fk_courses_category',
        'courses', 'categories',
        ['category_id'], ['id'],
        ondelete='SET NULL'
    )

def downgrade():
    op.drop_constraint('fk_courses_category', 'courses', type_='foreignkey')
    op.drop_column('courses', 'category_id')
