# --------------------------------------------------
# LOAD TEST ENV FIRST (CRITICAL)
# --------------------------------------------------
from dotenv import load_dotenv
load_dotenv(".env.test", override=True)

import sys, os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import pytest
from fastapi.testclient import TestClient
from datetime import time

from app.main import app
from app.database import get_db
from app.dependencies import get_current_user, oauth2_schema

from tests.test_database import create_test_db, TestingSessionLocal
from tests.pytest_reporter import collector

# --------------------------------------------------
# IMPORT MODELS (FK ORDER MATTERS)
# --------------------------------------------------
from app.models.subscription_plans_m import SubscriptionPlan
from app.models.organization_m import Organization
from app.models.role_m import Role
from app.models.user_m import User
from app.models.shift_m import Shift
from app.models.leavetype_m import LeaveType
from app.models.test_report_m import TestReport


# ==================================================
# FAKE AUTH USER (MATCHES REAL User MODEL)
# ==================================================
class FakeRole:
    id = 1
    name = "super_admin"


class FakeOrg:
    id = 1
    is_active = True


class FakeUser:
    id = 1
    first_name = "Test"
    last_name = "Admin"
    email = "admin@test.com"

    role_id = 1
    role = FakeRole()

    organization_id = 1
    organization = FakeOrg()

    is_org_admin = True
    inactive = False

    branch_id = None
    department_id = None
    designation = None
    biometric_id = "BIO_ADMIN"


# --------------------------------------------------
# DB OVERRIDE → COMMIT (API TESTS)
# --------------------------------------------------
def override_get_db_commit():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------
# AUTH OVERRIDE
# --------------------------------------------------
def override_get_current_user():
    return FakeUser()


app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[oauth2_schema] = lambda: "test-token"

# --------------------------------------------------
# FORCE BYPASS ALL PERMISSION CHECKERS
# --------------------------------------------------
def allow_all_permissions():
    return FakeUser()


for route in app.routes:
    if hasattr(route, "dependant"):
        for dep in route.dependant.dependencies:
            if dep.call and dep.call.__module__.startswith("app.permission_dependencies"):
                dep.call = allow_all_permissions


# --------------------------------------------------
# CREATE + SEED TEST DATABASE (ONCE)
# --------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    create_test_db()
    db = TestingSessionLocal()

    # Subscription Plan
    if not db.query(SubscriptionPlan).filter_by(id=1).first():
        db.add(
            SubscriptionPlan(
                id=1,
                name="Default Test Plan",
                description="Test plan",
                price_monthly=999,
                price_yearly=9999,
                branch_limit=5,
                user_limit=50,
                storage_limit_mb=5000,
                display_order=0,
                is_active=True,
                created_by="system"
            )
        )

    # Organization
    if not db.query(Organization).filter_by(id=1).first():
        db.add(Organization(id=1, name="Test Org", is_active=True))

    # Super Admin Role
    if not db.query(Role).filter_by(id=1).first():
        db.add(Role(id=1, name="super_admin"))

    # Admin User
    if not db.query(User).filter_by(id=1).first():
        db.add(
            User(
                id=1,
                first_name="Test",
                last_name="Admin",
                email="admin@test.com",
                hashed_password="dummy",
                role_id=1,
                organization_id=1,
                biometric_id="BIO_ADMIN",
                is_org_admin=True
            )
        )

    # Shift
    if not db.query(Shift).filter_by(id=1).first():
        db.add(
            Shift(
                id=1,
                created_by=1,
                shift_name="General Shift",
                shift_code="GEN",
                shift_type="regular",
                start_time=time(9, 0),
                end_time=time(17, 0),
                working_minutes=480,
                lag_minutes=60,
                status="active",
                is_week_off=0
            )
        )

    # Leave Types
    if not db.query(LeaveType).first():
        db.add_all([
            LeaveType(id=1, leave_type="Casual Leave", short_code="CL", is_active=True),
            LeaveType(id=2, leave_type="Sick Leave", short_code="SL", is_active=True),
        ])

    db.commit()
    db.close()
    yield


# --------------------------------------------------
# DB FIXTURE (USED BY TESTS)
# --------------------------------------------------
@pytest.fixture
def db():
    app.dependency_overrides[get_db] = override_get_db_commit
    yield from override_get_db_commit()


# --------------------------------------------------
# API CLIENT FIXTURE
# --------------------------------------------------
@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db_commit
    return TestClient(app)


# --------------------------------------------------
# PYTEST RESULT CAPTURE
# --------------------------------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        module = item.module.__name__
        if report.passed:
            collector.add_result(module, "passed", item.nodeid)
        elif report.failed:
            collector.add_result(module, "failed", item.nodeid, str(report.longrepr))


# --------------------------------------------------
# SAVE TEST REPORTS (APPEND ONLY)
# --------------------------------------------------
MAX_FAILURE_LENGTH = 60000

def pytest_sessionfinish(session, exitstatus):
    if not collector.results:
        return

    db = TestingSessionLocal()
    try:
        for module, data in collector.results.items():
            failures_text = None
            if data["failures"]:
                failures_text = "\n\n".join(data["failures"])[:MAX_FAILURE_LENGTH]

            db.add(
                TestReport(
                    module_name=module,
                    total_tests=data["total"],
                    passed=data["passed"],
                    failed=data["failed"],
                    failures=failures_text
                )
            )
        db.commit()
    finally:
        db.close()
