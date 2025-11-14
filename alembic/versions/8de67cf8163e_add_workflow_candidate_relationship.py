from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '8de67cf8163e'
down_revision = '4e321e6103bd'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    # --- Create candidate_documents table if it does not exist ---
    if 'candidate_documents' not in inspector.get_table_names():
        op.create_table(
            'candidate_documents',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('candidate_id', sa.Integer, nullable=False),
            sa.Column('document_type', sa.String(100), nullable=False),
            sa.Column('document_url', sa.String(255), nullable=False),
        )

    # --- Alter columns safely ---
    if 'candidate_documents' in inspector.get_table_names():
        op.alter_column('candidate_documents', 'document_type',
                        existing_type=mysql.VARCHAR(length=50),
                        type_=sa.String(length=100),
                        existing_nullable=False)
        op.alter_column('candidate_documents', 'document_url',
                        existing_type=mysql.VARCHAR(length=500),
                        type_=sa.String(length=255),
                        existing_nullable=False)

    # --- Create ix_candidates_id index safely ---
    if 'candidates' in inspector.get_table_names():
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('candidates')]
        if 'ix_candidates_id' not in existing_indexes:
            op.create_index('ix_candidates_id', 'candidates', ['id'], unique=False)


def downgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    # --- Drop ix_candidates_id index safely ---
    if 'candidates' in inspector.get_table_names():
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('candidates')]
        if 'ix_candidates_id' in existing_indexes:
            op.drop_index('ix_candidates_id', table_name='candidates')

    # --- Drop candidate_documents table safely ---
    if 'candidate_documents' in inspector.get_table_names():
        op.drop_table('candidate_documents')
