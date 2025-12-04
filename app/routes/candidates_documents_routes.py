from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.candidate_documents_m import CandidateDocument
from app.models.candidate_m import Candidate
from app.schemas.candidate_documents_schema import (
    CandidateDocumentCreate,
    CandidateDocumentUpdate,
    CandidateDocumentResponse
)

from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/candidate-documents", tags=["Candidate Documents"])

# Correct menu ID from Seeder
CANDIDATE_DOCS_MENU_ID = 65


# -------------------------
# ➕ CREATE DOCUMENT
# -------------------------
@router.post(
    "/",
    response_model=CandidateDocumentResponse,
    dependencies=[Depends(require_create_permission(CANDIDATE_DOCS_MENU_ID))]
)
def create_document(
    doc_data: CandidateDocumentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Check candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == doc_data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Check duplicate document
    existing_doc = db.query(CandidateDocument).filter(
        CandidateDocument.candidate_id == doc_data.candidate_id,
        CandidateDocument.document_name == doc_data.document_name
    ).first()

    if existing_doc:
        raise HTTPException(
            status_code=400,
            detail="Document already exists for this candidate"
        )

    new_doc = CandidateDocument(
        **doc_data.dict(),
        created_by=current_user.username,
        modified_by=current_user.username
    )

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


# -------------------------
# 📜 GET ALL DOCUMENTS
# -------------------------
@router.get(
    "/",
    response_model=List[CandidateDocumentResponse],
    dependencies=[Depends(require_view_permission(CANDIDATE_DOCS_MENU_ID))]
)
def get_all_documents(db: Session = Depends(get_db)):
    return db.query(CandidateDocument).all()


# -------------------------
# 📄 GET DOCUMENTS BY CANDIDATE
# -------------------------
@router.get(
    "/candidate/{candidate_id}",
    response_model=List[CandidateDocumentResponse],
    dependencies=[Depends(require_view_permission(CANDIDATE_DOCS_MENU_ID))]
)
def get_documents_by_candidate(candidate_id: int, db: Session = Depends(get_db)):
    docs = db.query(CandidateDocument).filter(
        CandidateDocument.candidate_id == candidate_id
    ).all()

    if not docs:
        raise HTTPException(status_code=404, detail="No documents found for this candidate")

    return docs


# -------------------------
# ✏️ UPDATE DOCUMENT
# -------------------------
@router.put(
    "/{document_id}",
    response_model=CandidateDocumentResponse,
    dependencies=[Depends(require_edit_permission(CANDIDATE_DOCS_MENU_ID))]
)
def update_document(
    document_id: int,
    update_data: CandidateDocumentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    doc = db.query(CandidateDocument).filter(CandidateDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Prevent duplicate type update
    if update_data.document_name:
        exists = db.query(CandidateDocument).filter(
            CandidateDocument.candidate_id == doc.candidate_id,
            CandidateDocument.document_name == update_data.document_name,
            CandidateDocument.id != document_id
        ).first()

        if exists:
            raise HTTPException(
                status_code=400,
                detail="Document already exists for this candidate"
            )

    # Update fields
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(doc, key, value)

    doc.modified_by = current_user.username

    db.commit()
    db.refresh(doc)
    return doc


# -------------------------
# ❌ DELETE DOCUMENT
# -------------------------
@router.delete(
    "/{document_id}",
    dependencies=[Depends(require_delete_permission(CANDIDATE_DOCS_MENU_ID))]
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    doc = db.query(CandidateDocument).filter(CandidateDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()

    return {"message": f"Document deleted successfully by {current_user.username}"}
