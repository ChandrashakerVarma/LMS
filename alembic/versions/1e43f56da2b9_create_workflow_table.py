"""create workflows table"""

from alembic import op
import sqlalchemy as sa

revision = '20251029_workflows'
down_revision = None  # or your last migration file
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'workflows',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('approval_required', sa.Boolean(), default=False),
        sa.Column('approver_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('approval_status', sa.String(50), default="Pending"),
        sa.Column('posting_id', sa.Integer(), sa.ForeignKey('job_postings.id'), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('workflows')
