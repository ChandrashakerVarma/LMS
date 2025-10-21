"""add first_name and last_name to users

Revision ID: 68ac6be60f74
Revises: ee8603062404
Create Date: 2025-10-16 12:19:23.649227
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '68ac6be60f74'
down_revision = 'ee8603062404'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns to users table
    op.add_column('users', sa.Column('first_name', sa.String(length=100), nullable=False))
    op.add_column('users', sa.Column('last_name', sa.String(length=100), nullable=True))
    
    # Optional: Fill first_name with some default if needed to avoid NOT NULL issues
    # op.execute("UPDATE users SET first_name = 'Unknown' WHERE first_name IS NULL;")
    
    # Drop old 'name' column
    op.drop_column('users', 'name')
    
    # Ensure all existing created_by_id in job_postings reference valid users
    # You may want to run this manually in MySQL before applying migration:
    # UPDATE job_postings SET created_by_id = 1 WHERE created_by_id NOT IN (SELECT id FROM users);
    
    # Then create foreign key
    op.create_foreign_key(
        'fk_job_postings_created_by',  # give a name to the FK
        'job_postings',                # source table
        'users',                       # referent table
        ['created_by_id'],              # local columns
        ['id']                         # remote columns
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the foreign key first
    op.drop_constraint('fk_job_postings_created_by', 'job_postings', type_='foreignkey')
    
    # Re-add old 'name' column
    op.add_column('users', sa.Column('name', mysql.VARCHAR(length=100), nullable=False))
    
    # Drop newly added columns
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
