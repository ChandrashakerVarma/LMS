"""add shift_roster_id to user_shifts

Revision ID: 5c1c56761ecd
Revises: 1d67ef805ef8
Create Date: 2025-11-08 23:32:59.156166
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = '5c1c56761ecd'
down_revision: Union[str, Sequence[str], None] = '1d67ef805ef8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_shifts', sa.Column('shift_roster_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_user_shifts_shift_roster_id',
        'user_shifts', 'shift_rosters',
        ['shift_roster_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_user_shifts_shift_roster_id', 'user_shifts', type_='foreignkey')
    op.drop_column('user_shifts', 'shift_roster_id')
