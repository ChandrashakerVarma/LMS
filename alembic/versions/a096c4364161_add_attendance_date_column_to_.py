"""add attendance_date column to attendances"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import Date, DateTime, func, text

# revision identifiers, used by Alembic.
revision = 'a096c4364161'
down_revision = 'dc2ae8ec8378'
branch_labels = None
depends_on = None


def upgrade():
    # 1️⃣ Add column as nullable first
    op.add_column('attendances', sa.Column('attendance_date', sa.Date(), nullable=True))

    # 2️⃣ Fill existing rows with punch_in date (safe default)
    conn = op.get_bind()
    conn.execute(text("""
        UPDATE attendances
        SET attendance_date = DATE(punch_in)
        WHERE attendance_date IS NULL
    """))

    # 3️⃣ Now alter column to be NOT NULL
    op.alter_column('attendances', 'attendance_date',
                    existing_type=sa.Date(),
                    nullable=False)


def downgrade():
    op.drop_column('attendances', 'attendance_date')
