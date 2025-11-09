import sys
import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv


# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Alembic Config object
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base and models
from app.database import Base  # keep only one Base import
from app.models import (
    role_m, user_m, course_m, Progress_m, video_m,
    QuizCheckpoint_m, QuizHistory_m, enrollment_m,
    shift_m, department_m, leavemaster_m,
    branch_m, category_m,week_day_m,
    organization_m, job_posting_m,
    jobrole_m,workflow_m,shift_roaster_m,shift_roaster_detail_m,permission_m,
    candidate_m,candidate_documents_m,
    user_shifts_m,shift_change_request_m,attendance_m
    )

# Metadata for autogenerate
target_metadata = Base.metadata

# Get DB URL
def get_database_url():
    return f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:3306/{os.getenv('DB_NAME')}"

# Offline migrations
def run_migrations_offline() -> None:
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# Online migrations
def run_migrations_online() -> None:
    connectable = create_engine(get_database_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# Run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
