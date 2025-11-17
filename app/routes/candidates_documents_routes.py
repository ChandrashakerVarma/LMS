from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.candidate_documents_m import CandidateDocument
from app.schema.candidate_documents_schema import (
    CandidateDocumentCreate,
    CandidateDocumentUpdate,
    CandidateDocumentOut
)

router = APIRouter(prefix="/candidate-documents", tags=["Candidate Documents"])


def serialize(doc: CandidateDocument):
    """Convert SQLAlchemy object → pure dict for Pydantic."""
    return {
        "id": doc.id,
        "candidate_id": doc.candidate_id,
        "document_type": doc.document_type,
        "document_url": doc.document_url
    }


# ------------------------------------------
# Create Document
# ------------------------------------------
@router.post("/", response_model=CandidateDocumentOut)
def create_document(doc_data: CandidateDocumentCreate, db: Session = Depends(get_db)):
    new_doc = CandidateDocument(**doc_data.dict())
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return serialize(new_doc)


# ------------------------------------------
# Get All Documents
# ------------------------------------------
@router.get("/", response_model=List[CandidateDocumentOut])
def get_all_documents(db: Session = Depends(get_db)):
    docs = db.query(CandidateDocument).all()
    return [serialize(doc) for doc in docs]


# ------------------------------------------
# Get Documents by Candidate
# ------------------------------------------
@router.get("/candidate/{candidate_id}", response_model=List[CandidateDocumentOut])
def get_documents_by_candidate(candidate_id: int, db: Session = Depends(get_db)):
    docs = db.query(CandidateDocument).filter(
        CandidateDocument.candidate_id == candidate_id
    ).all()
    return [serialize(doc) for doc in docs]


# ------------------------------------------
# Update Document
# ------------------------------------------
@router.put("/{document_id}", response_model=CandidateDocumentOut)
def update_document(document_id: int, update_data: CandidateDocumentUpdate, db: Session = Depends(get_db)):
    doc = db.query(CandidateDocument).filter(CandidateDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(doc, key, value)

    db.commit()
    db.refresh(doc)
    return serialize(doc)


# ------------------------------------------
# Delete Document
# ------------------------------------------
@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(CandidateDocument).filter(CandidateDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}
