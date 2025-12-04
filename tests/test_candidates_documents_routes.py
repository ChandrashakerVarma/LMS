from fastapi.testclient import TestClient
from io import BytesIO
from unittest.mock import patch
import pytest

from app.main import app
from app.database import get_db
from app.models.candidate_m import Candidate
from app.models.candidate_documents_m import CandidateDocument
from sqlalchemy.orm import Session

client = TestClient(app)


# -----------------------------------------------------------
# Dummy Role Object
# -----------------------------------------------------------
class DummyRole:
    name = "admin"


# -----------------------------------------------------------
# Dummy User With Required Attributes
# -----------------------------------------------------------
class DummyUser:
    id = 1
    username = "testuser"
    email = "test@example.com"
    first_name = "Test"
    last_name = "User"
    role = DummyRole()   # ✅ NOT STRING ANYMORE
    role_id = 1


@pytest.fixture(scope="function", autouse=True)
def override_user_dependency():
    from app.dependencies import get_current_user

    def fake_user():
        return DummyUser()

    app.dependency_overrides[get_current_user] = fake_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


# -----------------------------------------------------------
# DB Session
# -----------------------------------------------------------
@pytest.fixture
def db_session():
    db = next(get_db())
    yield db
    db.rollback()


# -----------------------------------------------------------
# Create Candidate
# -----------------------------------------------------------
@pytest.fixture
def create_candidate(db_session: Session):
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone_number="1234567890",
        job_posting_id=1
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    return candidate


# -----------------------------------------------------------
# CORRECT S3 MOCK
# -----------------------------------------------------------
@pytest.fixture(autouse=True)
def mock_s3_upload():
    import app.routes.candidates_documents_routes as route_module

    def fake_upload(file, folder="candidate_docs"):
        return f"https://fake-s3/{folder}/{file.filename}"

    with patch.object(route_module, "upload_file_to_s3", side_effect=fake_upload):
        yield


# -----------------------------------------------------------
# TEST: Upload Document
# -----------------------------------------------------------
def test_upload_candidate_document(create_candidate):
    file_content = BytesIO(b"dummy content")

    files = {"file": ("resume.pdf", file_content, "application/pdf")}

    data = {
        "candidate_id": str(create_candidate.id),
        "document_type": "Resume"
    }

    response = client.post("/candidate-documents/upload", files=files, data=data)
    assert response.status_code == 200

    resp = response.json()
    assert resp["candidate_id"] == create_candidate.id
    assert resp["document_type"] == "Resume"
    assert resp["document_url"].startswith("https://fake-s3/candidate_docs/")


# -----------------------------------------------------------
# TEST: Get All Documents
# -----------------------------------------------------------
def test_get_all_documents(db_session, create_candidate):
    doc = CandidateDocument(
        candidate_id=create_candidate.id,
        document_type="Resume",
        document_url="https://fake-s3/candidate_docs/sample.pdf"
    )
    db_session.add(doc)
    db_session.commit()

    response = client.get("/candidate-documents/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


# -----------------------------------------------------------
# TEST: Get Documents by Candidate
# -----------------------------------------------------------
def test_get_documents_by_candidate(db_session, create_candidate):
    doc = CandidateDocument(
        candidate_id=create_candidate.id,
        document_type="ID Proof",
        document_url="https://fake-s3/candidate_docs/id.pdf"
    )
    db_session.add(doc)
    db_session.commit()

    response = client.get(f"/candidate-documents/candidate/{create_candidate.id}")
    assert response.status_code == 200
    assert len(response.json()) >= 1


# -----------------------------------------------------------
# TEST: Update Document
# -----------------------------------------------------------
def test_update_document(db_session, create_candidate):
    doc = CandidateDocument(
        candidate_id=create_candidate.id,
        document_type="Resume",
        document_url="https://fake-s3/candidate_docs/sample.pdf"
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    response = client.put(
        f"/candidate-documents/{doc.id}",
        data={"document_type": "Updated Resume"},
        files={}
    )

    assert response.status_code == 200
    assert response.json()["document_type"] == "Updated Resume"


# -----------------------------------------------------------
# TEST: Delete Document
# -----------------------------------------------------------
def test_delete_document(db_session, create_candidate):
    doc = CandidateDocument(
        candidate_id=create_candidate.id,
        document_type="Certificate",
        document_url="https://fake-s3/candidate_docs/cert.pdf"
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    response = client.delete(f"/candidate-documents/{doc.id}")
    assert response.status_code == 200
    assert response.json()["message"].startswith("Document deleted successfully")
