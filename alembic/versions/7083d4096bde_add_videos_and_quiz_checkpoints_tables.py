"""Add videos and quiz checkpoints tables

Revision ID: 7083d4096bde
Revises: 5bf7b591c803
Create Date: 2025-09-09 15:59:52.600355
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = '7083d4096bde'
down_revision: Union[str, Sequence[str], None] = '5bf7b591c803'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    if 'videos' not in inspector.get_table_names():
        op.create_table(
            'videos',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('course_id', sa.Integer(), sa.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False),
            sa.Column('title', sa.String(length=150), nullable=True),
            sa.Column('youtube_url', sa.String(length=500), nullable=False),
            sa.Column('duration', sa.Float(), nullable=True),
        )
        op.create_index(op.f('ix_videos_id'), 'videos', ['id'], unique=False)

    if 'quiz_checkpoints' not in inspector.get_table_names():
        op.create_table(
            'quiz_checkpoints',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('video_id', sa.Integer(), sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False),
            sa.Column('timestamp', sa.Float(), nullable=False),
            sa.Column('required', sa.Boolean(), nullable=True),
        )
        op.create_index(op.f('ix_quiz_checkpoints_id'), 'quiz_checkpoints', ['id'], unique=False)

    if 'quiz_histories' not in inspector.get_table_names():
        op.create_table(
            'quiz_histories',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('checkpoint_id', sa.Integer(), sa.ForeignKey('quiz_checkpoints.id', ondelete='CASCADE'), nullable=False),
            sa.Column('score', sa.Float(), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )
        op.create_index(op.f('ix_quiz_histories_id'), 'quiz_histories', ['id'], unique=False)

    # Drop column if exists (PostgreSQL safe way)
    if 'youtube_url' in [c['name'] for c in inspector.get_columns('courses')]:
        op.drop_column('courses', 'youtube_url')


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Add column if it doesn’t exist
    if 'youtube_url' not in [c['name'] for c in inspector.get_columns('courses')]:
        op.add_column('courses', sa.Column('youtube_url', sa.String(length=500), nullable=False))

    # Drop tables and indexes only if they exist
    for table_name, index_name in [
        ('quiz_histories', 'ix_quiz_histories_id'),
        ('quiz_checkpoints', 'ix_quiz_checkpoints_id'),
        ('videos', 'ix_videos_id'),
    ]:
        if table_name in inspector.get_table_names():
            op.drop_index(index_name, table_name=table_name)
            op.drop_table(table_name)
