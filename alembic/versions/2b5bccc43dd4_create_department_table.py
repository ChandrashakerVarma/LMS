"""create department table

Revision ID: 2b5bccc43dd4
Revises: 35a15b1ce4e4
Create Date: 2025-09-25 13:10:20.136286
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2b5bccc43dd4'
down_revision = '35a15b1ce4e4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # Alter column safely
    op.alter_column('roles', 'name',
                    existing_type=sa.VARCHAR(length=100),
                    type_=sa.String(length=50),
                    existing_nullable=False)

    # Drop columns only if they exist
    conn = op.get_bind()
    columns_to_drop = ['status', 'code', 'created_at', 'permissions', 'updated_at', 'description']
    for col in columns_to_drop:
        exists = conn.execute(
            sa.text(f"""
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='roles' AND column_name='{col}'
            """)
        ).fetchone()
        if exists:
            op.drop_column('roles', col)

    # Create department table if it does not exist
    table_exists = conn.execute(sa.text("SELECT to_regclass('public.department')")).scalar()
    if not table_exists:
        op.create_table(
            'department',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
        )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    # Re-add columns if they do not exist
    columns_to_add = {
        'status': sa.Column('status', sa.SmallInteger, nullable=True),
        'code': sa.Column('code', sa.String(20), nullable=False),
        'created_at': sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=True),
        'permissions': sa.Column('permissions', sa.Text, nullable=True),
        'updated_at': sa.Column('updated_at', sa.DateTime, nullable=True),
        'description': sa.Column('description', sa.Text, nullable=True)
    }

    for col_name, col_def in columns_to_add.items():
        exists = conn.execute(
            sa.text(f"""
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='roles' AND column_name='{col_name}'
            """)
        ).fetchone()
        if not exists:
            op.add_column('roles', col_def)

    # Drop department table if exists
    table_exists = conn.execute(sa.text("SELECT to_regclass('public.department')")).scalar()
    if table_exists:
        op.drop_table('department')
