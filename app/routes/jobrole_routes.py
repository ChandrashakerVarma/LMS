from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.jobrole_m import JobRole
from app.schema.jobrole_schema import JobRoleCreate, JobRoleOut, JobRoleUpdate
from app.dependencies import require_admin, get_current_user

router = APIRouter(
    prefix="/job-roles",
    tags=["Job Roles"]
)

# -----------------------------------------------------------
#                  CREATE JOB ROLE  (ADMIN ONLY)
# -----------------------------------------------------------
@router.post("/", response_model=JobRoleOut)
def create_job_role(
    role: JobRoleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    new_role = JobRole(
        **role.dict(),
        created_by=current_user.first_name,  # only set created_by
        modified_by=None                      # do not set modified_by on create
    )

    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return JobRoleOut.from_orm(new_role)


# -----------------------------------------------------------
#                  GET ALL JOB ROLES
# -----------------------------------------------------------
@router.get("/", response_model=List[JobRoleOut])
def get_all_job_roles(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    roles = db.query(JobRole).all()
    return [JobRoleOut.from_orm(r) for r in roles]


# -----------------------------------------------------------
#                  GET JOB ROLE BY ID
# -----------------------------------------------------------
@router.get("/{role_id}", response_model=JobRoleOut)
def get_job_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Job role not found")

    return JobRoleOut.from_orm(role)


# -----------------------------------------------------------
#                 UPDATE JOB ROLE (ADMIN ONLY)
# -----------------------------------------------------------
@router.put("/{role_id}", response_model=JobRoleOut)
def update_job_role(
    role_id: int,
    role: JobRoleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    db_role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Job role not found")

    # Apply updates
    for key, value in role.dict(exclude_unset=True).items():
        setattr(db_role, key, value)

    # Update audit field
    db_role.modified_by = current_user.first_name

    db.commit()
    db.refresh(db_role)
    return JobRoleOut.from_orm(db_role)


# -----------------------------------------------------------
#                DELETE JOB ROLE (ADMIN ONLY)
# -----------------------------------------------------------
@router.delete("/{role_id}")
def delete_job_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    db_role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Job role not found")

    db.delete(db_role)
    db.commit()
    return {"detail": "Job role deleted successfully"}
