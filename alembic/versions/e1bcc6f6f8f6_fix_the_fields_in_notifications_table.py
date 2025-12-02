"""fix the fields in notifications table"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1bcc6f6f8f6'
down_revision = '35f613d4adbc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Fix NULL values for is_read before making it NOT NULL
    op.execute("UPDATE notifications SET is_read = 0 WHERE is_read IS NULL")

    # Step 2: Add created_by column
    op.add_column('notifications', sa.Column('created_by', sa.Integer(), nullable=False))

    # Step 3: Alter is_read to NOT NULL
    op.alter_column(
        'notifications',
        'is_read',
        existing_type=sa.Boolean(),
        nullable=False
    )

    # Step 4: Create the new foreign key for created_by
    op.create_foreign_key(
        None,
        'notifications',
        'users',
        ['created_by'],
        ['id']
    )

    # Step 5: Drop old user_id (ONLY after FK is created)
    op.drop_column('notifications', 'user_id')


def downgrade() -> None:
    # Step 1: Recreate user_id column
    op.add_column('notifications', sa.Column('user_id', sa.Integer(), nullable=True))

    # Step 2: Drop the created_by foreign key and column
    op.drop_constraint(None, 'notifications', type_='foreignkey')
    op.drop_column('notifications', 'created_by')

    # Step 3: Make is_read nullable again
    op.alter_column(
        'notifications',
        'is_read',
        existing_type=sa.Boolean(),
        nullable=True
    )
