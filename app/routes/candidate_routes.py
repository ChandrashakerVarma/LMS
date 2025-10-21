from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models.candidate_m import Candidate
from app.schema.candidate_schema import CandidateCreate, CandidateUpdate, CandidateOut
from app.s3_helper import upload_resume

router = APIRouter(prefix="/candidates", tags=["Candidates"])

# ✅ CREATE
@router.post("/", response_model=CandidateOut)
def create_candidate(
    first_name: str,
    last_name: str = None,
    email: str = None,
    phone_number: str = None,
    workflow_id: int = None,
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    resume_url = upload_resume(resume)

    candidate = Candidate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        workflow_id=workflow_id,
        applied_date=date.today(),
        resume_url=resume_url
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate

# ✅ READ (Single Candidate)
@router.get("/{candidate_id}", response_model=CandidateOut)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

# ✅ READ ALL
@router.get("/", response_model=list[CandidateOut])
def list_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).all()

# ✅ UPDATE
@router.put("/{candidate_id}", response_model=CandidateOut)
def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate = Depends(),
    resume: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Update fields
    for field, value in candidate_data.dict(exclude_unset=True).items():
        setattr(candidate, field, value)

    # Optional resume upload
    if resume:
        candidate.resume_url = upload_resume(resume)

    db.commit()
    db.refresh(candidate)
    return candidate

# ✅ DELETE
@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    db.delete(candidate)
    db.commit()
    return {"message": f"Candidate with ID {candidate_id} deleted successfully"}

