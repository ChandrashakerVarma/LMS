# D:\LMS\app\routes\ai_attendance_routes.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
import numpy as np
import cv2
import base64

from app.database import get_db
from app.dependencies import get_current_user
from app.models.attendance_m import Attendance

from app.ai_models.face_service import recognize_face_with_box
from app.ai_models.face_utils import recognize_user
from app.ai_models.insight_model import get_face_model

from app.utils.attendance_utils import check_location
from app.utils.attendance_anomaly_detector import detect_anomaly

router = APIRouter(prefix="/attendance", tags=["AI Attendance"])


# ------------------------------------------------------------------
# RESPECT USER attendance_mode
# ------------------------------------------------------------------
def resolve_attendance_location(db, current_user, lat, long):

    if current_user.attendance_mode == "WFH":
        return "WFH", True, 1.0

    if current_user.attendance_mode == "ANY":
        return "ANY", True, 1.0

    policy_status, allowed = check_location(
        db,
        current_user.id,
        current_user.branch_id,
        current_user.organization_id,
        lat,
        long,
    )

    gps_score = 1.0 if policy_status in ["OK", "INSIDE", "WFA"] else 0.4
    return policy_status, allowed, gps_score


# ------------------------------------------------------------------
# AI CHECK-IN
# ------------------------------------------------------------------
@router.post("/ai-checkin")
async def ai_checkin(
    lat: float,
    long: float,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    image_bytes = await file.read()

    recognized_user_id, processed_img, error_msg = recognize_face_with_box(
        image_bytes, db
    )

    if error_msg:
        raise HTTPException(400, error_msg)

    if recognized_user_id != current_user.id:
        raise HTTPException(
            403, f"Face mismatch. Expected: {current_user.id}, Detected: {recognized_user_id}"
        )

    _, img_encoded = cv2.imencode(".jpg", processed_img)
    face_preview_b64 = base64.b64encode(img_encoded).decode()

    policy_status, allowed, gps_score = resolve_attendance_location(
        db, current_user, lat, long
    )

    if not allowed:
        raise HTTPException(403, "Outside allowed attendance location")

    anomaly_status = detect_anomaly(
        similarity=1.0,
        gps_score=gps_score,
        avg_time_diff=0,
    )

    # --- required month field ---
    today_month = date.today().replace(day=1)

    entry = Attendance(
        user_id=current_user.id,
        check_in_time=datetime.utcnow(),
        check_in_lat=lat,
        check_in_long=long,
        gps_score=gps_score,
        location_status=policy_status,
        face_confidence=1.0,
        is_face_verified=True,
        anomaly_flag=anomaly_status,
        month=today_month,          # <-- required NOT NULL field
        shift_id=current_user.shift_roster_id,  # safe temporary mapping
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {
        "status": "success",
        "attendance_id": entry.id,
        "message": "AI check-in completed",
        "anomaly": anomaly_status,
        "face_preview": face_preview_b64,
    }


# ------------------------------------------------------------------
# AI CHECK-OUT
# ------------------------------------------------------------------
@router.post("/ai-checkout")
async def ai_checkout(
    lat: float,
    long: float,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    image_bytes = await file.read()
    frame = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(400, "Invalid image file")

    recognized_id = recognize_user(db, frame)

    if not recognized_id:
        raise HTTPException(403, "Face not recognized during checkout")

    if recognized_id != current_user.id:
        raise HTTPException(
            403, f"Face mismatch. Expected {current_user.id}, Detected {recognized_id}"
        )

    face_app = get_face_model()
    faces = face_app.get(frame)

    if len(faces) > 0:
        x1, y1, x2, y2 = faces[0].bbox.astype(int)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    _, img_encoded = cv2.imencode(".jpg", frame)
    face_preview_b64 = base64.b64encode(img_encoded).decode()

    policy_status, allowed, gps_score = resolve_attendance_location(
        db, current_user, lat, long
    )

    if not allowed:
        raise HTTPException(403, "Outside allowed location for punch-out")

    today = (
        db.query(Attendance)
        .filter(
            Attendance.user_id == current_user.id,
            Attendance.check_in_time != None,
            Attendance.punch_out == None,
        )
        .order_by(Attendance.id.desc())
        .first()
    )

    if not today:
        raise HTTPException(404, "No active attendance record for checkout")

    now = datetime.utcnow()
    worked_minutes = int((now - today.check_in_time).total_seconds() / 60)

    anomaly_status = detect_anomaly(
        similarity=1.0,
        gps_score=gps_score,
        avg_time_diff=0,
    )

    today.punch_out = now
    today.total_worked_minutes = worked_minutes
    today.status = "Present" if worked_minutes >= 240 else "Short Hours"
    today.location_status = policy_status
    today.gps_score = gps_score
    today.is_face_verified = True
    today.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(today)

    return {
        "status": "success",
        "attendance_id": today.id,
        "message": "AI punch-out successful",
        "worked_minutes": worked_minutes,
        "anomaly": anomaly_status,
        "face_preview": face_preview_b64,
    }
