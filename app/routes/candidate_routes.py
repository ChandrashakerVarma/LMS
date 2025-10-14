from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models.candidate_m import Candidate
from app.schema.candidate_schema import CandidateCreate, CandidateOut
from app.s3_helper import upload_resume

router = APIRouter(prefix="/candidates", tags=["Candidates"])


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
    # Upload resume to S3
    resume_url = upload_resume(resume)

    # Create candidate
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


@router.get("/{candidate_id}", response_model=CandidateOut)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.get("/", response_model=list[CandidateOut])
def list_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).all()
