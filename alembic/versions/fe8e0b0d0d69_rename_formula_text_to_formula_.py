"""rename formula_text to formula_expression fix

Revision ID: fe8e0b0d0d69
Revises: 44e67214b9ea
Create Date: 2025-10-14 16:39:29.329128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe8e0b0d0d69'
down_revision: Union[str, Sequence[str], None] = '44e67214b9ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("ALTER TABLE formulas CHANGE COLUMN formula_text formula_expression VARCHAR(255) NOT NULL;")

def downgrade():
    op.execute("ALTER TABLE formulas CHANGE COLUMN formula_expression formula_text VARCHAR(255) NOT NULL;")
