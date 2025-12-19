from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from typing import List

from app.database import get_db
from app.models.leaveconfig_m import LeaveConfig
from app.models.user_m import User

from app.schema.leaveconfig_schema import (
    LeaveConfigCreate,
    LeaveConfigUpdate,
    LeaveConfigResponse
)

from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

# Assign the correct MENU_ID for Leave Config module
MENU_ID = 45

router = APIRouter(prefix="/leave-config", tags=["Leave Config"])


# ============================================================
# CREATE Leave Config
# ============================================================
@router.post(
    "/",
    response_model=LeaveConfigResponse,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_leave_config(
    payload: LeaveConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave_config = LeaveConfig(
        **payload.model_dump(),
        created_by=current_user.first_name
    )

    db.add(leave_config)
    db.commit()
    db.refresh(leave_config)

    return leave_config


# ============================================================
# GET ALL Leave Config Entries
# ============================================================
@router.get(
    "/",
    response_model=List[LeaveConfigResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_leave_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(LeaveConfig).all()


# ============================================================
# GET Leave Config BY ID
# ============================================================
@router.get(
    "/{config_id}",
    response_model=LeaveConfigResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_leave_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config = db.query(LeaveConfig).filter(LeaveConfig.id == config_id).first()

    if not config:
        raise HTTPException(status_code=404, detail="Leave Config not found")

    return config


# ============================================================
# UPDATE Leave Config
# ============================================================
@router.put(
    "/{config_id}",
    response_model=LeaveConfigResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_leave_config(
    config_id: int,
    payload: LeaveConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config = db.query(LeaveConfig).filter(LeaveConfig.id == config_id).first()

    if not config:
        raise HTTPException(status_code=404, detail="Leave Config not found")

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(config, field, value)

    config.modified_by = current_user.first_name
    config.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(config)

    return config


# ============================================================
# DELETE Leave Config
# ============================================================
@router.delete(
    "/{config_id}",
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_leave_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config = db.query(LeaveConfig).filter(LeaveConfig.id == config_id).first()

    if not config:
        raise HTTPException(status_code=404, detail="Leave Config not found")

    db.delete(config)
    db.commit()

    return {"message": f"Leave Config deleted by {current_user.first_name}"}
