from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.job_description_m import JobDescription
from app.schemas.job_description_schema import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    JobDescriptionUpdate,
)

from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

router = APIRouter(
    prefix="/job-descriptions",
    tags=["Job Descriptions"]
)

MENU_ID = 63


# --------------------------------------------------------------
# ➕ CREATE JOB DESCRIPTION
# --------------------------------------------------------------
@router.post(
    "/",
    response_model=JobDescriptionResponse,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_job_description(
    payload: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_desc = JobDescription(
        **payload.model_dump(),
        created_by=current_user.first_name,
        modified_by=None
    )

    db.add(new_desc)
    db.commit()
    db.refresh(new_desc)

    return JobDescriptionResponse.model_validate(new_desc)


# --------------------------------------------------------------
# 📄 GET ALL JOB DESCRIPTIONS
# --------------------------------------------------------------
@router.get(
    "/",
    response_model=List[JobDescriptionResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_all_job_descriptions(db: Session = Depends(get_db)):
    descriptions = db.query(JobDescription).all()
    return [JobDescriptionResponse.model_validate(d) for d in descriptions]


# --------------------------------------------------------------
# 📌 GET JOB DESCRIPTION BY ID
# --------------------------------------------------------------
@router.get(
    "/{desc_id}",
    response_model=JobDescriptionResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_job_description(
    desc_id: int,
    db: Session = Depends(get_db)
):
    desc = db.query(JobDescription).filter(JobDescription.id == desc_id).first()
    if not desc:
        raise HTTPException(status_code=404, detail="Job description not found")

    return JobDescriptionResponse.model_validate(desc)


# --------------------------------------------------------------
# ✏️ UPDATE JOB DESCRIPTION
# --------------------------------------------------------------
@router.put(
    "/{desc_id}",
    response_model=JobDescriptionResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_job_description(
    desc_id: int,
    payload: JobDescriptionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_desc = db.query(JobDescription).filter(JobDescription.id == desc_id).first()
    if not db_desc:
        raise HTTPException(status_code=404, detail="Job description not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(db_desc, key, value)

    db_desc.modified_by = current_user.first_name
    db_desc.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_desc)

    return JobDescriptionResponse.model_validate(db_desc)


# --------------------------------------------------------------
# ❌ DELETE JOB DESCRIPTION
# --------------------------------------------------------------
@router.delete(
    "/{desc_id}",
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_job_description(
    desc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_desc = db.query(JobDescription).filter(JobDescription.id == desc_id).first()
    if not db_desc:
        raise HTTPException(status_code=404, detail="Job description not found")

    db.delete(db_desc)
    db.commit()

    return {"detail": f"Job description deleted by {current_user.first_name}"}
