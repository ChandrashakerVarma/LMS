import pytest
from io import BytesIO

from app.models.candidate_m import Candidate
from app.models.candidate_documents_m import CandidateDocument


# ==================================================
# FILE HELPER
# ==================================================
def create_test_file(name="resume.pdf", content=b"Dummy resume"):
    return (name, BytesIO(content), "application/pdf")


# ==================================================
# CANDIDATE FIXTURE
# ==================================================
@pytest.fixture
def candidate(db_session):
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email="john.doe@test.com",
        phone_number="9876543210",
        candidate_type="Fresher"
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    return candidate


# ==================================================
# TESTS
# ==================================================
def test_upload_candidate_document_success(client, candidate, db_session):
    response = client.post(
        "/candidate-documents/upload",
        data={"candidate_id": candidate.id, "document_type": "resume"},
        files={"file": create_test_file()}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["candidate_id"] == candidate.id

    doc = db_session.query(CandidateDocument).first()
    assert doc is not None
    assert doc.document_type == "resume"


def test_upload_duplicate_document_type(client, candidate):
    client.post(
        "/candidate-documents/upload",
        data={"candidate_id": candidate.id, "document_type": "resume"},
        files={"file": create_test_file()}
    )

    response = client.post(
        "/candidate-documents/upload",
        data={"candidate_id": candidate.id, "document_type": "resume"},
        files={"file": create_test_file()}
    )

    assert response.status_code == 400


def test_upload_candidate_not_found(client):
    response = client.post(
        "/candidate-documents/upload",
        data={"candidate_id": 9999, "document_type": "resume"},
        files={"file": create_test_file()}
    )

    assert response.status_code == 404


def test_get_all_documents(client, candidate):
    client.post(
        "/candidate-documents/upload",
        data={"candidate_id": candidate.id, "document_type": "resume"},
        files={"file": create_test_file()}
    )

    response = client.get("/candidate-documents/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_documents_by_candidate(client, candidate):
    client.post(
        "/candidate-documents/upload",
        data={"candidate_id": candidate.id, "document_type": "resume"},
        files={"file": create_test_file()}
    )

    response = client.get(f"/candidate-documents/candidate/{candidate.id}")
    assert response.status_code == 200
    assert response.json()[0]["candidate_id"] == candidate.id


def test_update_document_success(client, candidate, db_session):
    upload = client.post(
        "/candidate-documents/upload",
        data={"candidate_id": candidate.id, "document_type": "resume"},
        files={"file": create_test_file()}
    )
    doc_id = upload.json()["id"]

    response = client.put(
        f"/candidate-documents/{doc_id}",
        data={"document_type": "updated_resume"},
        files={"file": create_test_file("updated.pdf")}
    )

    assert response.status_code == 200

    doc = db_session.query(CandidateDocument).filter_by(id=doc_id).first()
    assert doc.document_type == "updated_resume"


def test_delete_document_success(client, candidate, db_session):
    upload = client.post(
        "/candidate-documents/upload",
        data={"candidate_id": candidate.id, "document_type": "resume"},
        files={"file": create_test_file()}
    )
    doc_id = upload.json()["id"]

    response = client.delete(f"/candidate-documents/{doc_id}")
    assert response.status_code == 200

    doc = db_session.query(CandidateDocument).filter_by(id=doc_id).first()
    assert doc is None
