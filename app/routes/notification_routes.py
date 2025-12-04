# app/routes/notification_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.notification_m import Notification
from app.schemas.notification_schema import NotificationCreate, NotificationResponse

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

MENU_ID = 62  # Notification menu ID


# ------------------------------------------------------
# CREATE NOTIFICATION
# ------------------------------------------------------
@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_notification(data: NotificationCreate, db: Session = Depends(get_db)):
    new_note = Notification(**data.model_dump())
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


# ------------------------------------------------------
# GET ALL NOTIFICATIONS
# ------------------------------------------------------
@router.get(
    "/",
    response_model=List[NotificationResponse],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_all_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).all()


# ------------------------------------------------------
# GET BY ID
# ------------------------------------------------------
@router.get(
    "/{note_id}",
    response_model=NotificationResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_notification(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Notification).filter(Notification.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")
    return note


# ------------------------------------------------------
# UPDATE NOTIFICATION
# ------------------------------------------------------
@router.put(
    "/{note_id}",
    response_model=NotificationResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_notification(note_id: int, data: NotificationCreate, db: Session = Depends(get_db)):
    note = db.query(Notification).filter(Notification.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")

    for key, value in data.model_dump().items():
        setattr(note, key, value)

    db.commit()
    db.refresh(note)
    return note


# ------------------------------------------------------
# DELETE NOTIFICATION
# ------------------------------------------------------
@router.delete(
    "/{note_id}",
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_notification(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Notification).filter(Notification.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(note)
    db.commit()

    return {"detail": "Notification deleted successfully"}
