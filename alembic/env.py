import sys
import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

# Make app importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base

# ----- IMPORT ALL MODELS SO ALEMBIC CAN SEE THEM -----
from app.models import (
    user_m, role_m, course_m, video_m, Progress_m,
    QuizCheckpoint_m, QuizHistory_m, enrollment_m,

    # HRMS
    shift_m, department_m, leavemaster_m, payroll_attendance_m,
    salary_structure_m, payroll_m, formula_m,
    attendance_m, attendance_punch_m,

    # Org structure
    organization_m, branch_m, category_m,

    # Job portal
    job_posting_m, candidate_m, candidate_documents_m,
    job_description_m,

    # Rosters
    shift_change_request_m, shift_roster_detail_m,
    shift_roster_m, user_shifts_m,

    # Auth & Permissions
    menu_m, role_right_m, permission_m,

    # Misc
    notification_m, week_day_m,

    # Subscription & Payments
    subscription_plans_m, add_on_m, organization_add_on_m, payment_m,

    # AI + attendance rules
    user_face_m, attendance_location_policy_m
)

target_metadata = Base.metadata


# ----------------------------------------------------
# DATABASE URL BUILDER (encodes password)
# ----------------------------------------------------
def get_database_url():
    db_user = os.getenv("DB_USER")
    raw_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")

    # Encode special chars (@)
    db_password = quote_plus(raw_password)

    url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/{db_name}"
    print("Using DATABASE_URL:", url)

    return url


# ----------------------------------------------------
# OFFLINE
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
# ONLINE
# ----------------------------------------------------
def run_migrations_online():
    connectable = create_engine(
        get_database_url(),
        poolclass=pool.NullPool,
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
