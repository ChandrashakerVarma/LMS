"""add ai attendance fields

Revision ID: 50b651ab66aa
Revises: final_merge
Create Date: 2025-12-08 17:06:43.568585
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50b651ab66aa'
down_revision: Union[str, Sequence[str], None] = 'final_merge'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("attendances") as batch_op:
        batch_op.add_column(sa.Column("shift_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("check_in_time", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("check_in_lat", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("check_in_long", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("gps_score", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("location_status", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("is_face_verified", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("face_confidence", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("check_in_image_path", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("punch_out", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("total_worked_minutes", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("status", sa.String(length=20), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("attendances") as batch_op:
        batch_op.drop_column("status")
        batch_op.drop_column("total_worked_minutes")
        batch_op.drop_column("punch_out")
        batch_op.drop_column("check_in_image_path")
        batch_op.drop_column("face_confidence")
        batch_op.drop_column("is_face_verified")
        batch_op.drop_column("location_status")
        batch_op.drop_column("gps_score")
        batch_op.drop_column("check_in_long")
        batch_op.drop_column("check_in_lat")
        batch_op.drop_column("check_in_time")
        batch_op.drop_column("shift_id")
