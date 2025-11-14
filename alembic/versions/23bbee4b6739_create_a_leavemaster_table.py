from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import mysql

# revision identifiers
revision: str = '23bbee4b6739'
down_revision: Union[str, Sequence[str], None] = '2702384eec9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()

    # --- Attendances Table ---
    if 'attendances' not in tables:
        op.create_table(
            'attendances',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
            sa.Column('punch_id', sa.String(100), nullable=False),
            sa.Column('first_punch', sa.DateTime, nullable=True),
            sa.Column('last_punch', sa.DateTime, nullable=True),
            sa.Column('shift_start', sa.DateTime, nullable=True),
            sa.Column('shift_end', sa.DateTime, nullable=True),
            sa.Column('latitude', sa.Float, nullable=True),
            sa.Column('longitude', sa.Float, nullable=True),
            sa.Column('status', sa.String(50), nullable=True),
            sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=True),
            sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=True),
        )
        op.create_index(op.f('ix_attendances_id'), 'attendances', ['id'], unique=False)

    # --- Shift Change Requests Table ---
    if 'shift_change_requests' not in tables:
        op.create_table(
            'shift_change_requests',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
            sa.Column('old_shift_id', sa.Integer, sa.ForeignKey('shifts.id'), nullable=True),
            sa.Column('new_shift_id', sa.Integer, sa.ForeignKey('shifts.id'), nullable=False),
            sa.Column('request_date', sa.Date, nullable=False),
            sa.Column('reason', sa.String(255), nullable=True),
            sa.Column('status', sa.String(20), nullable=True),
        )
        op.create_index(op.f('ix_shift_change_requests_id'), 'shift_change_requests', ['id'], unique=False)

    # --- Leave Master Table Alterations ---
    if 'leave_master' in tables:
        columns = [c['name'] for c in inspector.get_columns('leave_master')]

        # Modify existing columns
        if 'holiday' in columns:
            op.alter_column('leave_master', 'holiday',
                            existing_type=mysql.TINYINT(display_width=1),
                            type_=sa.String(100),
                            nullable=False)

        if 'description' in columns:
            op.alter_column('leave_master', 'description',
                            existing_type=mysql.TEXT(),
                            type_=sa.String(255),
                            existing_nullable=True)

        if 'user_id' in columns:
            op.alter_column('leave_master', 'user_id',
                            existing_type=mysql.INTEGER(),
                            nullable=False)

        if 'leave_type' in columns:
            op.alter_column('leave_master', 'leave_type',
                            existing_type=mysql.ENUM('CASUAL','SICK','EARNED','MATERNITY','BEREAVEMENT',
                                                     'STUDY','SPECIAL','UNPAID','PUBLIC_HOLIDAY','COMP_OFF'),
                            type_=sa.String(50),
                            existing_nullable=False)
        else:
            # If leave_type column doesn't exist, create it
            op.add_column('leave_master', sa.Column('leave_type', sa.String(50), nullable=False))

        if 'start_date' in columns:
            op.alter_column('leave_master', 'start_date', existing_type=sa.DATE(), nullable=True)

        if 'end_date' in columns:
            op.alter_column('leave_master', 'end_date', existing_type=sa.DATE(), nullable=True)
