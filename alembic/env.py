import sys
import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from urllib.parse import quote_plus
from dotenv import load_dotenv

<<<<<<< HEAD
# Load .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
=======
# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

>>>>>>> origin/main

# Alembic Config object
config = context.config

# Logging configuration
if config.config_file_name:
    fileConfig(config.config_file_name)

# ---- APP MODEL IMPORT SETUP ----
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base
from app.models import (
    role_m, user_m, course_m, Progress_m, video_m,
    QuizCheckpoint_m, QuizHistory_m, enrollment_m,
    shift_m, department_m, leavemaster_m, payroll_attendance_m,
    branch_m, category_m, organization_m, salary_structure_m, payroll_m,
    formula_m, permission_m, attendance_m, candidate_documents_m,
<<<<<<< HEAD
    candidate_m, job_posting_m, shift_change_request_m, shift_roster_detail_m,
    user_shifts_m, notification_m, menu_m, role_right_m,
    shift_roster_m, week_day_m, job_description_m,
    subscription_plans_m, add_on_m, organization_add_on_m, payment_m
=======
    candidate_m, job_posting_m, shift_change_request_m,shift_roster_detail_m,
    user_shifts_m,notification_m,menu_m,role_right_m,shift_roster_m,week_day_m,job_description_m,
    subscription_plans_m,add_on_m,organization_add_on_m,payment_m,
    attendance_punch_m
>>>>>>> origin/main
)

target_metadata = Base.metadata


# ----------------------------------------------------
# ✔ Safe Database URL Builder (handles @ inside password)
# ----------------------------------------------------
def get_database_url():
    db_user = os.getenv("DB_USER")
    raw_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("GITHUB_DB_HOST") or os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")

    # ⭐ FIX: Encode password so @ → %40
    db_password = quote_plus(raw_password)

    url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/{db_name}"

    # Print only for debugging (safe because encoded)
    print("Using DATABASE_URL:", url)

    return url


# ----------------------------------------------------
# OFFLINE MIGRATIONS
# ----------------------------------------------------
def run_migrations_offline():
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ----------------------------------------------------
# ONLINE MIGRATIONS
# ----------------------------------------------------
def run_migrations_online():
    connectable = create_engine(
        get_database_url(),
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# ----------------------------------------------------
# ENTRY POINT
# ----------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
