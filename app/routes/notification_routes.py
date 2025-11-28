# app/routes/notification_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.notification_m import Notification
<<<<<<< HEAD
from app.Schema.notification_schema import NotificationCreate, NotificationOut
=======
from app.schema.notification_schema import NotificationCreate, NotificationResponse

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)
>>>>>>> origin/main

router = APIRouter(prefix="/notifications", tags=["Notifications"])
MENU_ID = 62  # adjust if you have a different menu id for notifications


# Create Notification
@router.post("/", response_model=NotificationResponse, dependencies=[Depends(require_create_permission(MENU_ID))])
def create_notification(data: NotificationCreate, db: Session = Depends(get_db)):
    new_note = Notification(**data.dict())
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


# Get all notifications
@router.get("/", response_model=List[NotificationResponse], dependencies=[Depends(require_view_permission(MENU_ID))])
def get_all_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).all()


# Get notification by id
@router.get("/{note_id}", response_model=NotificationResponse, dependencies=[Depends(require_view_permission(MENU_ID))])
def get_notification(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Notification).filter(Notification.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")
    return note


# Update notification
@router.put("/{note_id}", response_model=NotificationResponse, dependencies=[Depends(require_edit_permission(MENU_ID))])
def update_notification(note_id: int, data: NotificationCreate, db: Session = Depends(get_db)):
    note = db.query(Notification).filter(Notification.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")

    for key, value in data.dict().items():
        setattr(note, key, value)

    db.commit()
    db.refresh(note)
    return note


# Delete notification
@router.delete("/{note_id}", dependencies=[Depends(require_delete_permission(MENU_ID))])
def delete_notification(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Notification).filter(Notification.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(note)
    db.commit()
<<<<<<< HEAD

    return {"detail": "Notification deleted successfully"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.notification_m import Notification
from app.Schema.notification_schema import NotificationCreate, NotificationOut

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# -------------------- CREATE --------------------
@router.post("/", response_model=NotificationOut)
def create_notification(data: NotificationCreate, db: Session = Depends(get_db)):
    new_note = Notification(**data.dict())
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


# -------------------- GET ALL --------------------
@router.get("/", response_model=List[NotificationOut])
def get_all_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).all()


# -------------------- GET BY ID --------------------
@router.get("/{note_id}", response_model=NotificationOut)
def get_notification(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Notification).filter(Notification.id == note_id).first()
    if not note:
        raise HTTPException(404, "Notification not found")
    return note


# -------------------- UPDATE --------------------
@router.put("/{note_id}", response_model=NotificationOut)
def update_notification(
    note_id: int,
    data: NotificationCreate,
    db: Session = Depends(get_db)
):
    note = db.query(Notification).filter(Notification.id == note_id).first()

    if not note:
        raise HTTPException(404, "Notification not found")

    for key, value in data.dict().items():
        setattr(note, key, value)

    db.commit()
    db.refresh(note)
    return note


# -------------------- DELETE --------------------
@router.delete("/{note_id}")
def delete_notification(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Notification).filter(Notification.id == note_id).first()

    if not note:
        raise HTTPException(404, "Notification not found")

    db.delete(note)
    db.commit()

=======
>>>>>>> origin/main
    return {"detail": "Notification deleted successfully"}
