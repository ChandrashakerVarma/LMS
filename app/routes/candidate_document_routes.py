from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.candidate_document_m import CandidateDocument
from app.schema.candidate_document_schema import CandidateDocumentCreate, CandidateDocumentResponse
from app.s3_helper import upload_resume, delete_file_from_s3  # assuming delete helper exists

router = APIRouter(
    prefix="/candidate-documents",
    tags=["Candidate Documents"]
)

# Upload multiple documents for a candidate
@router.post("/{candidate_id}/upload", response_model=List[CandidateDocumentResponse])
async def upload_candidate_documents(
    candidate_id: int,
    files: List[UploadFile] = File(...),
    document_types: List[str] = File(...),
    db: Session = Depends(get_db)
):
    if len(files) != len(document_types):
        raise HTTPException(status_code=400, detail="Each file must have a corresponding document type")

    uploaded_docs = []
    for i, file in enumerate(files):
        doc_type = document_types[i]
        # Upload to S3
        file_url = upload_resume(file, folder=f"candidates/{candidate_id}")
        
        # Save in DB
        candidate_doc = CandidateDocument(
            candidate_id=candidate_id,
            document_type=doc_type,
            document_url=file_url
        )
        db.add(candidate_doc)
        db.commit()
        db.refresh(candidate_doc)
        uploaded_docs.append(candidate_doc)

    return uploaded_docs

# Get all documents for a candidate
@router.get("/{candidate_id}", response_model=List[CandidateDocumentResponse])
def get_candidate_documents(candidate_id: int, db: Session = Depends(get_db)):
    docs = db.query(CandidateDocument).filter(CandidateDocument.candidate_id == candidate_id).all()
    return docs

# Update a candidate document
@router.put("/{document_id}", response_model=CandidateDocumentResponse)
async def update_candidate_document(
    document_id: int,
    file: UploadFile = File(...),
    document_type: str = File(...),
    db: Session = Depends(get_db)
):
    doc = db.query(CandidateDocument).filter(CandidateDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete old file from S3
    delete_file_from_s3(doc.document_url)

    # Upload new file
    file_url = upload_resume(file, folder=f"candidates/{doc.candidate_id}")
    
    # Update DB
    doc.document_type = document_type
    doc.document_url = file_url
    db.commit()
    db.refresh(doc)
    return doc

# Delete a candidate document
@router.delete("/{document_id}", response_model=dict)
def delete_candidate_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(CandidateDocument).filter(CandidateDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from S3
    delete_file_from_s3(doc.document_url)
    
    # Delete from DB
    db.delete(doc)
    db.commit()
    return {"detail": "Document deleted successfully"}
