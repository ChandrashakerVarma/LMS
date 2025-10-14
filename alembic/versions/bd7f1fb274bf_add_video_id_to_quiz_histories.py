"""add video_id to quiz_histories

Revision ID: bd7f1fb274bf
Revises: 0f81e38f3df2
Create Date: 2025-10-06 16:08:32.449556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd7f1fb274bf'
down_revision: Union[str, Sequence[str], None] = '0f81e38f3df2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add video_id column
    op.add_column('quiz_histories', sa.Column('video_id', sa.Integer(), nullable=False))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_quiz_histories_video',    # constraint name
        'quiz_histories',             # source table
        'videos',                     # target table
        ['video_id'],                 # source column
        ['id'],                       # target column
        ondelete='CASCADE'
    )

def downgrade():
    # Drop foreign key
    op.drop_constraint('fk_quiz_histories_video', 'quiz_histories', type_='foreignkey')
    
    # Drop column
    op.drop_column('quiz_histories', 'video_id')
