from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2b4f59dcdbf2'
down_revision = '1aac06f04dc2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add department_id column to users
    op.add_column('users', sa.Column('department_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        None,                 # let Alembic generate a name
        'users',              # source table
        'departments',        # target table
        ['department_id'],    # local column
        ['id']                # remote column
    )


def downgrade() -> None:
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'department_id')
