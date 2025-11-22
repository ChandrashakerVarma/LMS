from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.candidate_documents_m import CandidateDocument
from app.models.candidate_m import Candidate
from app.schema.candidate_documents_schema import (
    CandidateDocumentCreate,
    CandidateDocumentUpdate,
    CandidateDocumentOut
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/candidate-documents", tags=["Candidate Documents"])


def serialize(doc: CandidateDocument):
    """Convert SQLAlchemy object → dict for Pydantic."""
    return {
        "id": doc.id,
        "candidate_id": doc.candidate_id,
        "document_type": doc.document_type,
        "document_url": doc.document_url,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
        "created_by": doc.created_by,
        "modified_by": doc.modified_by,
    }

@router.post("/", response_model=CandidateDocumentOut)
def create_document(
    doc_data: CandidateDocumentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == doc_data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Prevent duplicate document type
    existing = db.query(CandidateDocument).filter(
        CandidateDocument.candidate_id == doc_data.candidate_id,
        CandidateDocument.document_type == doc_data.document_type
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Document type already exists for this candidate"
        )

    # Create
    new_doc = CandidateDocument(
        **doc_data.dict(),
        created_by=current_user.first_name,
        modified_by=current_user.first_name
    )

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return serialize(new_doc)

@router.get("/", response_model=List[CandidateDocumentOut])
def get_all_documents(db: Session = Depends(get_db)):
    docs = db.query(CandidateDocument).all()
    return [serialize(doc) for doc in docs]

@router.get("/candidate/{candidate_id}", response_model=List[CandidateDocumentOut])
def get_documents_by_candidate(candidate_id: int, db: Session = Depends(get_db)):
    docs = db.query(CandidateDocument).filter(
        CandidateDocument.candidate_id == candidate_id
    ).all()
    return [serialize(doc) for doc in docs]

@router.put("/{document_id}", response_model=CandidateDocumentOut)
def update_document(
    document_id: int,
    update_data: CandidateDocumentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    doc = db.query(CandidateDocument).filter(CandidateDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Prevent duplicate document type update
    if update_data.document_type:
        exists = db.query(CandidateDocument).filter(
            CandidateDocument.candidate_id == doc.candidate_id,
            CandidateDocument.document_type == update_data.document_type,
            CandidateDocument.id != document_id
        ).first()

        if exists:
            raise HTTPException(
                status_code=400,
                detail="Document type already exists for this candidate"
            )

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(doc, key, value)

    doc.modified_by = current_user.first_name

    db.commit()
    db.refresh(doc)
    return serialize(doc)

@router.delete("/{document_id}")
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
    return {"message": f"Document deleted successfully by {current_user.first_name}"}
