"""create job_roles table"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic
revision = '20251029_job_roles'
down_revision = None  # or your last migration ID
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'job_roles',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('required_skills', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    )


def downgrade() -> None:
    op.drop_table('job_roles')
