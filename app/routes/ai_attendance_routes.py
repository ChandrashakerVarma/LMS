from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import cv2
import numpy as np
import tempfile

from app.database import get_db
from app.dependencies import get_current_user
from app.models.attendance_m import Attendance
from app.utils.face_utils import recognize_face
from app.utils.attendance_utils import check_location
from app.s3_helper import upload_file_to_s3

router = APIRouter(prefix="/attendance", tags=["AI Attendance"])


# ------------------------------------------------------------
# AI CHECK-IN WITH FACE + LOCATION POLICY
# ------------------------------------------------------------
@router.post("/ai-checkin")
async def ai_checkin(
    lat: float,
    long: float,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # --------------------------------------------------------
    # 1. Read Image Bytes
    # --------------------------------------------------------
    file_bytes = await file.read()

    np_arr = np.frombuffer(file_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(400, "Invalid image input")

    # --------------------------------------------------------
    # 2. FACE MATCHING
    # --------------------------------------------------------
    recognized_user_id = recognize_face(frame)

    if recognized_user_id != current_user.id:
        raise HTTPException(
            401, f"Face mismatch. Expected {current_user.id}, got {recognized_user_id}"
        )

    # --------------------------------------------------------
    # 3. LOCATION CHECK (GeoFence)
    # --------------------------------------------------------
    policy_status, allowed = check_location(
        db,
        current_user.id,
        getattr(current_user, "branch_id", None),
        getattr(current_user, "organization_id", None),
        lat,
        long,
    )

    if not allowed:
        raise HTTPException(403, "Outside allowed geofence location")

    # --------------------------------------------------------
    # 4. OPTIONAL: UPLOAD IMAGE TO S3
    # --------------------------------------------------------
    try:
        key = f"attendance/{current_user.id}/{datetime.utcnow().timestamp()}.jpg"
        image_path = upload_file_to_s3(file_bytes, key)
    except Exception:
        image_path = None  # In case S3 is disabled or fails

    # --------------------------------------------------------
    # 5. SAVE ATTENDANCE ENTRY
    # --------------------------------------------------------
    entry = Attendance(
        user_id=current_user.id,
        check_in_time=datetime.utcnow(),
        check_in_lat=lat,
        check_in_long=long,
        location_status=policy_status,
        is_face_verified=True,
        check_in_image_path=image_path,
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {
        "status": "success",
        "attendance_id": entry.id,
        "message": "AI check-in completed",
    }
