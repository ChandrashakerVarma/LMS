from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.candidate_m import Candidate
from app.schema.candidate_schema import CandidateResponse, CandidateUpdate
from app.s3_helper import upload_file_to_s3
from app.utils.email_ses import send_email_ses
from app.utils.email_templates_utils import render_email
from app.permission_dependencies import require_edit_permission

router = APIRouter(prefix="/candidates", tags=["Candidates"])

# ---------------------------------------------------------
# APPLY FOR A JOB  (Create Candidate)
# ---------------------------------------------------------
@router.post("/", response_model=CandidateResponse)
async def apply_candidate(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    job_posting_id: int = Form(...),
    resume: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    resume_url = None
    # Upload resume if provided
    if resume:
        resume_url = upload_file_to_s3(resume, folder="candidate_resumes")

    # Create candidate entry
    candidate = Candidate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone,
        job_posting_id=job_posting_id,
        applied_date=datetime.utcnow().date(),
        resume_url=resume_url
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return candidate


# ---------------------------------------------------------
# GET ALL CANDIDATES
# ---------------------------------------------------------
@router.get("/", response_model=List[CandidateResponse])
def get_all_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).all()


# ---------------------------------------------------------
# GET CANDIDATE BY ID
# ---------------------------------------------------------
@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


# ---------------------------------------------------------
# UPDATE CANDIDATE
# ---------------------------------------------------------

@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    job_posting_id: Optional[int] = Form(None),
    resume: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Upload new resume if provided
    if resume:
        resume_url = upload_file_to_s3(resume, folder="candidate_resumes")
        candidate.resume_url = resume_url

    # Update remaining fields only if provided
    if first_name:
        candidate.first_name = first_name
    if last_name:
        candidate.last_name = last_name
    if email:
        candidate.email = email
    if phone:
        candidate.phone_number = phone
    if job_posting_id:
        candidate.job_posting_id = job_posting_id

    db.commit()
    db.refresh(candidate)
    return candidate



# ---------------------------------------------------------
# DELETE CANDIDATE
# ---------------------------------------------------------
@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    db.delete(candidate)
    db.commit()
    return {"message": "Candidate deleted successfully"}


# ---------------------------------------------------------
# UPDATE CANDIDATE STATUS AND SEND EMAIL
# ---------------------------------------------------------
@router.put(
    "/{candidate_id}/status/{new_status}",
    response_model=CandidateResponse,
    dependencies=[Depends(require_edit_permission)]
)
async def update_candidate_status(
    candidate_id: int,
    new_status: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if new_status not in ["Accepted", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = new_status
    db.commit()
    db.refresh(candidate)

    job_posting = candidate.job_posting
    job_title = job_posting.job_description.title if job_posting and job_posting.job_description else "Job"

    if new_status == "Accepted":
        html_body = render_email(
            "accepted_email.html",
            {
                "candidate_name": f"{candidate.first_name} {candidate.last_name}",
                "job_title": job_title,
                "location": job_posting.location if job_posting else None,
                "interview_datetime": None,
                "organization_name": "Your Organization Name",
                "organization_logo": None,
            },
        )
        background_tasks.add_task(
            send_email_ses,
            subject=f"Your Application for {job_title} is Accepted",
            body=html_body,
            to_email=candidate.email
        )

    elif new_status == "Rejected":
        html_body = render_email(
            "rejected_email.html",
            {
                "candidate_name": f"{candidate.first_name} {candidate.last_name}",
                "job_title": job_title,
                "organization_name": "Your Organization Name",
                "organization_logo": None,
            },
        )
        background_tasks.add_task(
            send_email_ses,
            subject=f"Update on Your Application for {job_title}",
            body=html_body,
            to_email=candidate.email
        )

    return candidate
