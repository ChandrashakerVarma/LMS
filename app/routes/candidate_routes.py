from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
)
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, List

from app.database import get_db
from app.models.candidate_m import Candidate
from app.models.job_posting_m import JobPosting
from app.models.user_m import User
from app.schema.candidate_schema import CandidateResponse
from app.s3_helper import upload_file_to_s3
from app.utils.email_ses import send_email_ses
from app.utils.email_templates_utils import render_email
from app.permission_dependencies import (
    require_view_permission,
    require_edit_permission
)

router = APIRouter(prefix="/candidates", tags=["Candidates"])
MENU_ID = 61
# ============================================================
# 1️⃣ APPLY CANDIDATE (CREATE)
# ============================================================
@router.post("/", response_model=CandidateResponse)
async def apply_candidate(
    # Basic
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    job_posting_id: int = Form(...),
    candidate_type: str = Form(...),

    # Education / skills
    highest_qualification: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),

    # Fresher
    college_name: Optional[str] = Form(None),
    graduation_year: Optional[int] = Form(None),
    course: Optional[str] = Form(None),
    cgpa: Optional[str] = Form(None),

    # Experienced
    total_experience: Optional[str] = Form(None),
    previous_company: Optional[str] = Form(None),
    last_ctc: Optional[str] = Form(None),

    # Languages
    telugu_level: Optional[str] = Form(None),
    english_level: Optional[str] = Form(None),
    hindi_level: Optional[str] = Form(None),

    # Personal
    gender: Optional[str] = Form(None),
    date_of_birth: Optional[date] = Form(None),

    # Address
    address_line1: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),

    resume: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    job = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    if candidate_type not in ["fresher", "experienced"]:
        raise HTTPException(status_code=400, detail="Invalid candidate_type")

    if candidate_type == "fresher" and not all([college_name, graduation_year, course, cgpa]):
        raise HTTPException(status_code=400, detail="Provide all fresher details")

    if candidate_type == "experienced" and not all([total_experience, previous_company, last_ctc]):
        raise HTTPException(status_code=400, detail="Provide all experience details")

    # Safe last_ctc conversion
    last_ctc_value = int(last_ctc) if last_ctc not in ["", None, "null"] else None

    resume_url = upload_file_to_s3(resume, "candidate_resumes") if resume else None

    candidate = Candidate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        job_posting_id=job_posting_id,
        candidate_type=candidate_type,

        highest_qualification=highest_qualification,
        skills=skills,

        college_name=college_name,
        graduation_year=graduation_year,
        course=course,
        cgpa=cgpa,

        total_experience=total_experience,
        previous_company=previous_company,
        last_ctc=last_ctc_value,

        telugu_level=telugu_level,
        english_level=english_level,
        hindi_level=hindi_level,

        gender=gender,
        date_of_birth=date_of_birth,

        address_line1=address_line1,
        city=city,
        state=state,
        country=country,
        pincode=pincode,

        resume_url=resume_url,
        applied_date=datetime.utcnow().date()
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


# ============================================================
# 2️⃣ GET ALL CANDIDATES
# ============================================================
@router.get("/", response_model=List[CandidateResponse])
def get_all_candidates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    if current_user.role.name == "super_admin":
        return db.query(Candidate).all()

    return (
        db.query(Candidate)
        .join(JobPosting)
        .filter(JobPosting.organization_id == current_user.organization_id)
        .all()
    )


# ============================================================
# 3️⃣ GET CANDIDATE BY ID
# ============================================================
@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


# ============================================================
# 4️⃣ GET CANDIDATES BY JOB
# ============================================================
@router.get("/job/{job_posting_id}", response_model=List[CandidateResponse])
def get_candidates_by_job(
    job_posting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(MENU_ID))
):
    return db.query(Candidate).filter(Candidate.job_posting_id == job_posting_id).all()


# ============================================================
# 5️⃣ UPDATE CANDIDATE
# ============================================================
@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),

    highest_qualification: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),

    college_name: Optional[str] = Form(None),
    graduation_year: Optional[int] = Form(None),
    course: Optional[str] = Form(None),
    cgpa: Optional[str] = Form(None),

    total_experience: Optional[str] = Form(None),
    previous_company: Optional[str] = Form(None),
    last_ctc: Optional[int] = Form(None),

    telugu_level: Optional[str] = Form(None),
    english_level: Optional[str] = Form(None),
    hindi_level: Optional[str] = Form(None),

    gender: Optional[str] = Form(None),
    date_of_birth: Optional[date] = Form(None),

    address_line1: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),

    resume: Optional[UploadFile] = File(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(MENU_ID))
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if resume:
        candidate.resume_url = upload_file_to_s3(resume, "candidate_resumes")

    for field, value in locals().items():
        if field not in ["candidate_id", "resume", "db", "current_user"] and value is not None:
            setattr(candidate, field, value)

    db.commit()
    db.refresh(candidate)
    return candidate


# ============================================================
# 6️⃣ DELETE CANDIDATE
# ============================================================
@router.delete("/{candidate_id}")
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(MENU_ID))
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    db.delete(candidate)
    db.commit()
    return {"message": "Candidate deleted successfully"}


# ============================================================
# 7️⃣ UPDATE STATUS + EMAIL
# ============================================================
@router.put("/{candidate_id}/status/{new_status}", response_model=CandidateResponse)
async def update_candidate_status(
    candidate_id: int,
    new_status: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(MENU_ID))
):
    if new_status not in ["Accepted", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = new_status
    db.commit()
    db.refresh(candidate)

    subject = "🎉 You are selected!" if new_status == "Accepted" else "Application Update"
    template = "accepted_email.html" if new_status == "Accepted" else "rejected_email.html"

    html_body = render_email(template, {
        "candidate_name": f"{candidate.first_name} {candidate.last_name}"
    })

    background_tasks.add_task(send_email_ses, subject, html_body, candidate.email)
    return candidate
