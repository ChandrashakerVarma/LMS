"""fix organization-branch relationship

Revision ID: 2bb544b81e38
Revises: 5b2bafb247ee
Create Date: 2025-09-26 16:06:08.984644
"""
from alembic import op
from sqlalchemy import inspect, String
from sqlalchemy.dialects import postgresql

revision = '2bb544b81e38'
down_revision = '5b2bafb247ee'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # 1️⃣ Adjust description column length
    op.alter_column('organizations', 'description',
                    existing_type=postgresql.VARCHAR(length=500),
                    type_=String(length=255),
                    existing_nullable=True)

    # 2️⃣ Drop foreign key on branch_id if exists
    fks = inspector.get_foreign_keys('organizations')
    for fk in fks:
        if 'branch_id' in fk['constrained_columns']:
            op.drop_constraint(fk['name'], 'organizations', type_='foreignkey')

    # 3️⃣ Drop unnecessary columns safely
    for col in ['updated_at', 'created_at', 'branch_id']:
        if col in [c['name'] for c in inspector.get_columns('organizations')]:
            op.drop_column('organizations', col)


def downgrade() -> None:
    from sqlalchemy import Column, Integer, DateTime, text
    # 1️⃣ Add branch_id, created_at, updated_at columns back
    op.add_column('organizations', Column('branch_id', Integer(), nullable=True))
    op.add_column('organizations', Column('created_at', DateTime(), server_default=text('now()'), nullable=False))
    op.add_column('organizations', Column('updated_at', DateTime(), server_default=text('now()'), nullable=False))

    # 2️⃣ Recreate foreign key for branch_id
    op.create_foreign_key(None, 'organizations', 'branches', ['branch_id'], ['id'], ondelete='SET NULL')

    # 3️⃣ Restore description column length
    op.alter_column('organizations', 'description',
                    existing_type=String(length=255),
                    type_=postgresql.VARCHAR(length=500),
                    existing_nullable=True)
