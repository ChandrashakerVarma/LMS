"""Add question column to quiz_checkpoints safely

Revision ID: c7a0af826fdd
Revises: 009d55d2ebca
Create Date: 2025-09-09 17:07:30.268888
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c7a0af826fdd'
down_revision: Union[str, Sequence[str], None] = '009d55d2ebca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # quiz_checkpoints table
    qc_columns = [c['name'] for c in inspector.get_columns('quiz_checkpoints')]
    if 'question' not in qc_columns:
        op.add_column('quiz_checkpoints', sa.Column('question', sa.String(length=500), nullable=False))
    if 'required' in qc_columns:
        op.drop_column('quiz_checkpoints', 'required')

    # quiz_histories table
    qh_columns = [c['name'] for c in inspector.get_columns('quiz_histories')]
    if 'answer' not in qh_columns:
        op.add_column('quiz_histories', sa.Column('answer', sa.String(length=500), nullable=False))
    if 'result' not in qh_columns:
        op.add_column('quiz_histories', sa.Column('result', sa.String(length=50), nullable=False))
    if 'score' in qh_columns:
        op.drop_column('quiz_histories', 'score')
    if 'completed_at' in qh_columns:
        op.drop_column('quiz_histories', 'completed_at')


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # quiz_histories table
    qh_columns = [c['name'] for c in inspector.get_columns('quiz_histories')]
    if 'completed_at' not in qh_columns:
        op.add_column('quiz_histories', sa.Column('completed_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=False))
    if 'score' not in qh_columns:
        op.add_column('quiz_histories', sa.Column('score', mysql.FLOAT(), nullable=True))
    if 'result' in qh_columns:
        op.drop_column('quiz_histories', 'result')
    if 'answer' in qh_columns:
        op.drop_column('quiz_histories', 'answer')

    # quiz_checkpoints table
    qc_columns = [c['name'] for c in inspector.get_columns('quiz_checkpoints')]
    if 'required' not in qc_columns:
        op.add_column('quiz_checkpoints', sa.Column('required', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    if 'question' in qc_columns:
        op.drop_column('quiz_checkpoints', 'question')
