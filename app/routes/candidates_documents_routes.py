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

# Create a new document
@router.post("/", response_model=CandidateDocumentOut)
def create_document(doc_data: CandidateDocumentCreate, db: Session = Depends(get_db)):
    new_doc = CandidateDocument(**doc_data.dict())
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


# Get all documents
@router.get("/", response_model=List[CandidateDocumentOut])
def get_all_documents(db: Session = Depends(get_db)):
    return db.query(CandidateDocument).all()


# Get documents by candidate_id
@router.get("/candidate/{candidate_id}", response_model=List[CandidateDocumentOut])
def get_documents_by_candidate(candidate_id: int, db: Session = Depends(get_db)):
    docs = db.query(CandidateDocument).filter(CandidateDocument.candidate_id == candidate_id).all()
    if not docs:
        raise HTTPException(status_code=404, detail="No documents found for this candidate")
    return docs


# Update a document
@router.put("/{document_id}", response_model=CandidateDocumentOut)
def update_document(document_id: int, update_data: CandidateDocumentUpdate, db: Session = Depends(get_db)):
    doc = db.query(CandidateDocument).filter(CandidateDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(doc, key, value)

    db.commit()
    db.refresh(doc)
    return doc


# Delete a document
@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(CandidateDocument).filter(CandidateDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}
