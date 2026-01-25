from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import settings

# 🔥 FORCE IMPORT ALL MODELS (VERY IMPORTANT)
from app.models.user_m import User
from app.models.role_m import Role
from app.models.organization_m import Organization
from app.models.shift_m import Shift
from app.models.leavemaster_m import LeaveMaster
from app.models.leavetype_m import LeaveType
from app.models.leaveconfig_m import LeaveConfig
from app.models.leave_balance_m import LeaveBalance
from app.models.permission_m import Permission
from app.models.holiday_m import Holiday
from app.models.enrollment_m import Enrollment
from app.models.subscription_plans_m import SubscriptionPlan
from app.models.branch_m import Branch
from app.models.role_m import Role
from app.models.role_right_m import RoleRight
from app.models.menu_m import Menu
from app.models.shift_m import Shift
from app.models.shift_change_request_m import ShiftChangeRequest
from app.models.shift_roster_m import ShiftRoster
from app.models.shift_roster_detail_m import ShiftRosterDetail
from app.models.week_day_m import WeekDay
from app.models.user_shifts_m import UserShift
from app.models.test_report_m import TestReport


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def create_test_db():
    """
    Reset all business tables
    BUT keep test_reports history forever.
    """
    print("🚀 Preparing TEST DB (preserving test_reports history):", settings.DATABASE_URL)

    # Drop all tables except test_reports
    for table in reversed(Base.metadata.sorted_tables):
        if table.name != "test_reports":
            table.drop(bind=engine, checkfirst=True)

    # Recreate missing tables
    Base.metadata.create_all(bind=engine)
