"""adding extra fields to notifications table

Revision ID: 6701ba9dbcd7
Revises: a51406b58f4a
Create Date: 2025-11-29 15:41:53.299604
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers
revision = '6701ba9dbcd7'
down_revision = 'a51406b58f4a'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    notif_columns = [c['name'] for c in inspector.get_columns('notifications')]
    org_columns = [c['name'] for c in inspector.get_columns('organizations')]

    # Add columns only if they don't exist
    if 'user_id' not in notif_columns:
        op.add_column('notifications', sa.Column('user_id', sa.Integer(), nullable=True))
        op.create_foreign_key(
            'notifications_user_id_fkey',
            'notifications', 'users',
            ['user_id'], ['id'],
            ondelete='SET NULL'
        )

    if 'is_read' not in notif_columns:
        op.add_column('notifications', sa.Column('is_read', sa.Boolean(), nullable=True))

    if 'created_at' not in notif_columns:
        op.add_column('notifications', sa.Column(
            'created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))

    op.alter_column('notifications', 'message',
                    existing_type=mysql.VARCHAR(length=255),
                    nullable=False)

    if 'organization_logo' not in org_columns:
        op.add_column('organizations', sa.Column('organization_logo', sa.String(length=255), nullable=True))


def downgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    notif_columns = [c['name'] for c in inspector.get_columns('notifications')]
    org_columns = [c['name'] for c in inspector.get_columns('organizations')]

    if 'organization_logo' in org_columns:
        op.drop_column('organizations', 'organization_logo')

    if 'user_id' in notif_columns:
        op.drop_constraint('notifications_user_id_fkey', 'notifications', type_='foreignkey')
        op.drop_column('notifications', 'user_id')

    if 'is_read' in notif_columns:
        op.drop_column('notifications', 'is_read')

    if 'created_at' in notif_columns:
        op.drop_column('notifications', 'created_at')

    op.alter_column('notifications', 'message',
                    existing_type=mysql.VARCHAR(length=255),
                    nullable=True)
