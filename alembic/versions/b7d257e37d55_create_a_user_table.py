"""create a user table safely

Revision ID: b7d257e37d55
Revises: 453459e95439
Create Date: 2025-09-23 19:10:26.516689
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'b7d257e37d55'
down_revision: Union[str, Sequence[str], None] = '453459e95439'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    conn = op.get_bind()
    return conn.dialect.has_table(conn, table_name)


def upgrade() -> None:
    """Upgrade schema safely."""
    
    # Courses table
    if not table_exists('courses'):
        op.create_table(
            'courses',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=150), nullable=False),
            sa.Column('instructor', sa.String(length=100), nullable=False),
            sa.Column('level', sa.String(length=50), nullable=False),
            sa.Column('duration', sa.Float(), nullable=True),
            sa.Column('price', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('title')
        )
        op.create_index(op.f('ix_courses_id'), 'courses', ['id'], unique=False)

    # Roles table
    if not table_exists('roles'):
        op.create_table(
            'roles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
        op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)

    # Users table
    if not table_exists('users'):
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=100), nullable=False),
            sa.Column('hashed_password', sa.String(length=200), nullable=False),
            sa.Column('role_id', sa.Integer(), nullable=True),
            sa.Column('date_of_birth', sa.DateTime(), nullable=True),
            sa.Column('joining_date', sa.DateTime(), nullable=True),
            sa.Column('relieving_date', sa.DateTime(), nullable=True),
            sa.Column('address', sa.String(length=500), nullable=True),
            sa.Column('photo', sa.String(length=200), nullable=True),
            sa.Column('designation', sa.String(length=100), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.Column('inactive', sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Videos table
    if not table_exists('videos'):
        op.create_table(
            'videos',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('course_id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=150), nullable=True),
            sa.Column('youtube_url', sa.String(length=500), nullable=False),
            sa.Column('duration', sa.Float(), nullable=True),
            sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_videos_id'), 'videos', ['id'], unique=False)

    # Enrollments table
    if not table_exists('enrollments'):
        op.create_table(
            'enrollments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('course_id', sa.Integer(), nullable=False),
            sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_enrollments_id'), 'enrollments', ['id'], unique=False)

    # Progress table
    if not table_exists('progress'):
        op.create_table(
            'progress',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('course_id', sa.Integer(), nullable=False),
            sa.Column('watched_minutes', sa.Float(), nullable=True),
            sa.Column('progress_percentage', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_progress_id'), 'progress', ['id'], unique=False)

    # Quiz checkpoints
    if not table_exists('quiz_checkpoints'):
        op.create_table(
            'quiz_checkpoints',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('video_id', sa.Integer(), nullable=False),
            sa.Column('timestamp', sa.Float(), nullable=False),
            sa.Column('question', sa.String(length=500), nullable=False),
            sa.Column('choices', sa.String(length=500), nullable=False),
            sa.Column('correct_answer', sa.String(length=50), nullable=False),
            sa.Column('required', sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_quiz_checkpoints_id'), 'quiz_checkpoints', ['id'], unique=False)

    # Quiz histories
    if not table_exists('quiz_histories'):
        op.create_table(
            'quiz_histories',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('checkpoint_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('course_id', sa.Integer(), nullable=False),
            sa.Column('question', sa.String(length=500), nullable=True),
            sa.Column('answer', sa.String(length=500), nullable=True),
            sa.Column('result', sa.String(length=50), nullable=True),
            sa.ForeignKeyConstraint(['checkpoint_id'], ['quiz_checkpoints.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_quiz_histories_id'), 'quiz_histories', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    tables = [
        'quiz_histories', 'quiz_checkpoints', 'progress',
        'enrollments', 'videos', 'users', 'roles', 'courses'
    ]
    for table in tables:
        if table_exists(table):
            op.drop_table(table)
