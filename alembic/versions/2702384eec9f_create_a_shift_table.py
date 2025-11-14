from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import mysql
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '2702384eec9f'
down_revision: Union[str, Sequence[str], None] = 'd0b9370aa848'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # Only create attendances table if it doesn't exist
    if 'attendances' not in inspector.get_table_names():
        op.create_table(
            'attendances',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('punch_id', sa.String(length=100), nullable=False),
            sa.Column('first_punch', sa.DateTime(), nullable=True),
            sa.Column('last_punch', sa.DateTime(), nullable=True),
            sa.Column('shift_start', sa.DateTime(), nullable=True),
            sa.Column('shift_end', sa.DateTime(), nullable=True),
            sa.Column('latitude', sa.Float(), nullable=True),
            sa.Column('longitude', sa.Float(), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        )

    # Only create shift_change_requests if it doesn't exist
    if 'shift_change_requests' not in inspector.get_table_names():
        op.create_table(
            'shift_change_requests',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('old_shift_id', sa.Integer(), sa.ForeignKey('shifts.id'), nullable=True),
            sa.Column('new_shift_id', sa.Integer(), sa.ForeignKey('shifts.id'), nullable=False),
            sa.Column('request_date', sa.Date(), nullable=False),
            sa.Column('reason', sa.String(length=255), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=True),
        )

    # Add other alter_column / index / constraint commands here as usual
    # They usually won't fail if the column/index/constraint already exists

def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    if 'shift_change_requests' in inspector.get_table_names():
        op.drop_table('shift_change_requests')

    if 'attendances' in inspector.get_table_names():
        op.drop_table('attendances')

    # Reverse other schema changes here as needed
