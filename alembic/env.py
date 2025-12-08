import sys
import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

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
    candidate_m, job_posting_m, shift_change_request_m, shift_roster_detail_m,
    user_shifts_m, notification_m, menu_m, role_right_m,
    shift_roster_m, week_day_m, job_description_m,
    subscription_plans_m, add_on_m, organization_add_on_m, payment_m,
    attendance_punch_m
)

target_metadata = Base.metadata
