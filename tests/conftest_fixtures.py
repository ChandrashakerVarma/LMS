# tests/conftest.py
import uuid
import pytest
from app.config import settings
from app.models.organization_m import Organization
from app.models.branch_m import Branch
from app.models.job_description_m import JobDescription
from app.models.candidate_m import Candidate

# ======================================================
# AWS MOCK SETTINGS
# ======================================================
settings.AWS_REGION = getattr(settings, "AWS_REGION_RESUME", "eu-north-1")
settings.AWS_BUCKET_NAME = getattr(settings, "BUCKET_NAME_RESUME", "test-bucket")
settings.AWS_ACCESS_KEY_ID = getattr(settings, "AWS_ACCESS_KEY_ID_RESUME", "test-access-key")
settings.AWS_SECRET_ACCESS_KEY = getattr(
    settings, "AWS_SECRET_ACCESS_KEY_RESUME", "test-secret-key"
)

# ======================================================
# ORGANIZATION
# ======================================================
@pytest.fixture
def organization(db_session):
    org = Organization(
        name=f"Test Org {uuid.uuid4()}",
        subscription_status="active",
        branch_limit=5,
        user_limit=10,
        storage_limit_mb=1000,
        current_storage_mb=0,
        current_branches=0,
        current_users=0,
        total_amount_paid=0,
        is_active=True
    )
    db_session.add(org)
    db_session.flush()
    return org

# ======================================================
# BRANCH
# ======================================================
@pytest.fixture
def branch(db_session, organization):
    branch = Branch(
        name=f"Bangalore Branch {uuid.uuid4()}",
        organization_id=organization.id
    )
    db_session.add(branch)
    db_session.flush()
    return branch

# ======================================================
# JOB DESCRIPTION
# ======================================================
@pytest.fixture
def job_description(db_session):
    jd = JobDescription(
        title=f"Python Developer {uuid.uuid4()}",
        description="FastAPI + SQLAlchemy",
        required_skills="Python, FastAPI"
    )
    db_session.add(jd)
    db_session.flush()
    return jd

# ======================================================
# CANDIDATE
# ======================================================
@pytest.fixture
def candidate(db_session):
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email=f"john.{uuid.uuid4()}@test.com",
        phone_number="9876543210",
        candidate_type="Fresher"
    )
    db_session.add(candidate)
    db_session.flush()
    return candidate

# ======================================================
# 🔧 FIXED S3 MOCK (ONLY CHANGE)
# ======================================================
@pytest.fixture(autouse=True)
def mock_s3_upload(monkeypatch):
    def fake_upload(file, folder="candidate_docs"):
        return f"https://test-bucket.s3.amazonaws.com/{folder}/{file.filename}"

    # ✅ PATCH REAL MODULE WHERE FUNCTION IS DEFINED
    monkeypatch.setattr(
        "app.s3_helper.upload_file_to_s3",
        fake_upload
    )
