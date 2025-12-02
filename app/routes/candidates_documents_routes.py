from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.candidate_documents_m import CandidateDocument
from app.models.candidate_m import Candidate
from app.schema.candidate_documents_schema import (
    CandidateDocumentResponse,
    CandidateDocumentUpdate
)

from app.s3_helper import upload_file_to_s3
from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/candidate-documents", tags=["Candidate Documents"])
MENU_ID = 65

# Upload Document
@router.post(
    "/upload",
    response_model=CandidateDocumentResponse,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
async def upload_candidate_document(
    candidate_id: int = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check if candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Check if document of this type already exists for the candidate
    existing_doc = db.query(CandidateDocument).filter(
        CandidateDocument.candidate_id == candidate_id,
        CandidateDocument.document_type == document_type
    ).first()
    if existing_doc:
        raise HTTPException(
            status_code=400, 
            detail=f"Document of type '{document_type}' already exists for this candidate"
        )

    # Upload file to S3
    document_url = upload_file_to_s3(file, folder="candidate_docs")
    created_by_name = f"{current_user.first_name} {current_user.last_name}"

    # Create new document
    new_doc = CandidateDocument(
        candidate_id=candidate_id,
        document_type=document_type,
        document_url=document_url,
        created_by=created_by_name
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


# Get All Documents

@router.get(
    "/",
    response_model=List[CandidateDocumentResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_all_documents(db: Session = Depends(get_db)):
    return db.query(CandidateDocument).all()

# Get Documents by Candidate
@router.get(
    "/candidate/{candidate_id}",
    response_model=List[CandidateDocumentResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_documents_by_candidate(candidate_id: int, db: Session = Depends(get_db)):
    docs = db.query(CandidateDocument).filter(CandidateDocument.candidate_id == candidate_id).all()
    if not docs:
        raise HTTPException(status_code=404, detail="No documents found")
    return docs

# Update Document
@router.put(
    "/{document_id}",
    response_model=CandidateDocumentResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_document(
    document_id: int,
    data: CandidateDocumentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    doc = db.query(CandidateDocument).filter(CandidateDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if data.document_type:
        doc.document_type = data.document_type
    if data.document_url:
        doc.document_url = data.document_url

    doc.modified_by = f"{current_user.first_name} {current_user.last_name}"
    db.commit()
    db.refresh(doc)
    return doc

# Delete Document
@router.delete(
    "/{document_id}",
    dependencies=[Depends(require_delete_permission(MENU_ID))]
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
    deleted_by_name = f"{current_user.first_name} {current_user.last_name}"
    return {"message": f"Document deleted successfully by {deleted_by_name}"}
