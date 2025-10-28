"""rename formula_text to formula_expression

Revision ID: 44e67214b9ea
Revises: 3dbaf8673fa1
Create Date: 2025-10-14 15:59:27.799568
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '44e67214b9ea'
down_revision: Union[str, Sequence[str], None] = '3dbaf8673fa1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('formulas', 'formula_text', new_column_name='formula_expression')

def downgrade() -> None:
    op.alter_column('formulas', 'formula_expression', new_column_name='formula_text')
