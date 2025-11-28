from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.jobrole_m import JobRole
from app.Schema.jobrole_schema import JobRoleCreate, JobRoleOut, JobRoleUpdate
from app.dependencies import require_admin, get_current_user

# ------------- PERMISSION IMPORTS (Your required style) -------------
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(
    prefix="/job-roles",
    tags=["Job Roles"]
)

MENU_ID = 62   # <<==== your menu id


# -----------------------------------------------------------
#                  CREATE JOB ROLE  (ADMIN ONLY)
# -----------------------------------------------------------
@router.post("/", response_model=JobRoleOut)
def create_job_role(
    role: JobRoleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_create_permission(MENU_ID))   # <---- permission added
):
    new_role = JobRole(
        **role.dict(),
        created_by=current_user.first_name,
        modified_by=None
    )

    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return JobRoleOut.from_orm(new_role)


# -----------------------------------------------------------
#                  GET ALL JOB ROLES  (VIEW)
# -----------------------------------------------------------
@router.get("/", response_model=List[JobRoleOut])
def get_all_job_roles(
    db: Session = Depends(get_db),
    current_user=Depends(require_view_permission(MENU_ID))   # <---- permission added
):
    roles = db.query(JobRole).all()
    return [JobRoleOut.from_orm(r) for r in roles]


# -----------------------------------------------------------
#                  GET JOB ROLE BY ID (VIEW)
# -----------------------------------------------------------
@router.get("/{role_id}", response_model=JobRoleOut)
def get_job_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_view_permission(MENU_ID))   # <---- permission added
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
    current_user=Depends(require_edit_permission(MENU_ID))   # <---- permission added
):
    db_role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Job role not found")

    for key, value in role.dict(exclude_unset=True).items():
        setattr(db_role, key, value)

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
    current_user=Depends(require_delete_permission(MENU_ID))   # <---- permission added
):
    db_role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Job role not found")

    db.delete(db_role)
    db.commit()
    return {"detail": "Job role deleted successfully"}
