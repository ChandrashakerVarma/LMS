import sys
import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alembic config
config = context.config

# Logging
if config.config_file_name:
    fileConfig(config.config_file_name)

# Import Base and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base
from app.models import (
    role_m, user_m, course_m, Progress_m, video_m,
    QuizCheckpoint_m, QuizHistory_m, enrollment_m,
    shift_m, department_m, leavemaster_m, payroll_attendance_m,
    branch_m, category_m, organization_m, salary_structure_m, payroll_m,
    formula_m, permission_m, attendance_m, candidate_documents_m,
    candidate_m, job_posting_m, jobrole_m, shift_change_request_m,
    user_shifts_m, workflow_m, notification_m,menu_m,role_right_m
)

target_metadata = Base.metadata

# Read DB config
def get_database_url():
    # ⭐ IMPORTANT FIX ⭐
    # When running on GitHub Actions → DB_HOST must be "mysql"
    db_host = os.getenv("GITHUB_DB_HOST") or os.getenv("DB_HOST")

    return f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{db_host}:3306/{os.getenv('DB_NAME')}"

# Offline migrations
def run_migrations_offline():
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# Online migrations
def run_migrations_online():
    connectable = create_engine(
        get_database_url(),
        poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# Entry point
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
