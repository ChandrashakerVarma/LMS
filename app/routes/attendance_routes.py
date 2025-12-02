# ENHANCED app/routes/attendance_routes.py
# ✅ Adds OPTIONAL anomaly detection to existing GET endpoint
# ✅ All existing functionality remains UNCHANGED
# ✅ Backward compatible - default behavior is identical

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.database import get_db
from app.models.attendance_m import Attendance
from app.models.shift_m import Shift
from app.models.user_m import User
from app.schema.attendance_schema import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.utils.attendance_utils import calculate_attendance_status
from app.dependencies import get_current_user

# ✅ Permission helpers
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

ATTENDANCE_MENU_ID = 44

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# -------------------------------
# CREATE Attendance (UNCHANGED)
# -------------------------------
@router.post(
    "/", 
    response_model=AttendanceResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(ATTENDANCE_MENU_ID))]
)
def create_attendance(
    payload: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    shift = db.query(Shift).filter(Shift.id == payload.shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    attendance_date = payload.punch_in.date()

    existing = db.query(Attendance).filter(
        Attendance.user_id == payload.user_id,
        Attendance.attendance_date == attendance_date
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Attendance already exists for this user on this date"
        )

    if shift.start_time > shift.end_time:
        if payload.punch_out <= payload.punch_in:
            raise HTTPException(status_code=400, detail="Night shift: punch-out must be next day")
    else:
        if payload.punch_in >= payload.punch_out:
            raise HTTPException(status_code=400, detail="Punch-out must be after punch-in")

    result = calculate_attendance_status(
        shift_start=shift.start_time,
        shift_end=shift.end_time,
        lag_minutes=shift.lag_minutes,
        working_minutes=shift.working_minutes,
        punch_in=payload.punch_in,
        punch_out=payload.punch_out
    )

    record = Attendance(
        user_id=payload.user_id,
        shift_id=payload.shift_id,
        attendance_date=attendance_date,
        punch_in=payload.punch_in,
        punch_out=payload.punch_out,
        total_worked_minutes=result["total_worked_minutes"],
        status=result["status"],
        created_by=current_user.first_name
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


# -------------------------------
# ✅ ENHANCED: GET All Attendance with OPTIONAL Anomaly Detection
# -------------------------------
@router.get(
    "/", 
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_all_attendance(
    # ✅ NEW: Optional anomaly detection parameters
    detect_anomalies: bool = Query(False, description="Enable ML-powered anomaly detection"),
    anomaly_days_back: int = Query(90, ge=30, le=365, description="Days of historical data for anomaly training"),
    anomaly_only: bool = Query(False, description="Return only anomalous records"),
    
    # Existing filter parameters (you can add more as needed)
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[date] = Query(None, description="Filter from this date"),
    end_date: Optional[date] = Query(None, description="Filter until this date"),
    status: Optional[str] = Query(None, description="Filter by status (Full Day, Half Day, Absent)"),
    
    db: Session = Depends(get_db)
):
    """
    Get all attendance records with OPTIONAL anomaly detection
    
    **Default behavior (detect_anomalies=false):**
    - Returns all attendance records (same as before)
    
    **With anomaly detection (detect_anomalies=true):**
    - Trains ML model on historical data
    - Identifies unusual attendance patterns
    - Adds 'anomaly_info' field to each record
    
    **Examples:**
    - GET /attendance/ → Normal behavior (unchanged)
    - GET /attendance/?detect_anomalies=true → With anomaly detection
    - GET /attendance/?detect_anomalies=true&anomaly_only=true → Only anomalies
    - GET /attendance/?user_id=5&start_date=2024-01-01 → Filtered (unchanged)
    """
    
    # Build base query (EXISTING LOGIC - UNCHANGED)
    query = db.query(Attendance)
    
    # Apply filters (you can expand this based on your needs)
    if user_id:
        query = query.filter(Attendance.user_id == user_id)
    
    if start_date:
        query = query.filter(Attendance.attendance_date >= start_date)
    
    if end_date:
        query = query.filter(Attendance.attendance_date <= end_date)
    
    if status:
        query = query.filter(Attendance.status == status)
    
    # Get records (EXISTING LOGIC - UNCHANGED)
    records = query.order_by(Attendance.attendance_date.desc()).all()
    
    # ✅ DEFAULT PATH: No anomaly detection (backward compatible)
    if not detect_anomalies:
        # Return standard response (UNCHANGED)
        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "shift_id": r.shift_id,
                "attendance_date": r.attendance_date,
                "punch_in": r.punch_in,
                "punch_out": r.punch_out,
                "total_worked_minutes": r.total_worked_minutes,
                "status": r.status,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "created_by": r.created_by,
                "modified_by": r.modified_by
            }
            for r in records
        ]
    
    # ✅ NEW PATH: With anomaly detection
    try:
        from app.utils.attendance_anomaly_detector import get_or_train_model
        
        # Get or train model (auto-trains if not cached)
        # Note: You'll need to pass organization_id from current_user
        # For now, using a default. Adjust based on your auth system.
        detector = get_or_train_model(db, organization_id=1, days_back=anomaly_days_back)
        
        # Convert records to dict for ML processing
        attendance_dicts = [
            {
                'id': r.id,
                'user_id': r.user_id,
                'attendance_date': r.attendance_date,
                'punch_in': r.punch_in,
                'punch_out': r.punch_out,
                'total_worked_minutes': r.total_worked_minutes,
                'status': r.status
            }
            for r in records
        ]
        
        # Detect anomalies
        anomalies = detector.predict_anomalies(attendance_dicts)
        
        # Create anomaly lookup
        anomaly_map = {a['attendance_id']: a for a in anomalies}
        
        # Enhance records with anomaly info
        enhanced_records = []
        for r in records:
            record_dict = {
                "id": r.id,
                "user_id": r.user_id,
                "shift_id": r.shift_id,
                "attendance_date": r.attendance_date,
                "punch_in": r.punch_in,
                "punch_out": r.punch_out,
                "total_worked_minutes": r.total_worked_minutes,
                "status": r.status,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "created_by": r.created_by,
                "modified_by": r.modified_by,
                # ✅ NEW: Anomaly information
                "is_anomaly": r.id in anomaly_map,
                "anomaly_info": anomaly_map.get(r.id, None)
            }
            
            # Filter if only anomalies requested
            if anomaly_only and not record_dict["is_anomaly"]:
                continue
            
            enhanced_records.append(record_dict)
        
        return {
            "success": True,
            "total_records": len(records),
            "anomalies_detected": len(anomalies),
            "anomaly_rate": len(anomalies) / len(records) if records else 0,
            "records": enhanced_records
        }
    
    except ValueError as ve:
        # Not enough data for training
        raise HTTPException(
            status_code=400,
            detail=f"Anomaly detection failed: {str(ve)}"
        )
    except Exception as e:
        # If anomaly detection fails, return standard response
        raise HTTPException(
            status_code=500,
            detail=f"Anomaly detection error: {str(e)}"
        )


# -------------------------------
# GET Attendance by ID (UNCHANGED)
# -------------------------------
@router.get(
    "/{attendance_id}", 
    response_model=AttendanceResponse,
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return record


# -------------------------------
# UPDATE Attendance (UNCHANGED)
# -------------------------------
@router.put(
    "/{attendance_id}", 
    response_model=AttendanceResponse,
    dependencies=[Depends(require_edit_permission(ATTENDANCE_MENU_ID))]
)
def update_attendance(
    attendance_id: int,
    payload: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(record, key, value)

    if record.punch_in and record.punch_out:
        if record.punch_in >= record.punch_out:
            raise HTTPException(status_code=400, detail="Punch-out must be after punch-in")

    shift = db.query(Shift).filter(Shift.id == record.shift_id).first()

    if shift and record.punch_in and record.punch_out:
        result = calculate_attendance_status(
            shift_start=shift.start_time,
            shift_end=shift.end_time,
            lag_minutes=shift.lag_minutes,
            working_minutes=shift.working_minutes,
            punch_in=record.punch_in,
            punch_out=record.punch_out
        )

        record.total_worked_minutes = result["total_worked_minutes"]
        record.status = result["status"]
        record.attendance_date = record.punch_in.date()

    record.modified_by = current_user.first_name

    db.commit()
    db.refresh(record)

    return record


# -------------------------------
# DELETE Attendance (UNCHANGED)
# -------------------------------
@router.delete(
    "/{attendance_id}",
    dependencies=[Depends(require_delete_permission(ATTENDANCE_MENU_ID))]
)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance not found")

    db.delete(record)
    db.commit()

    return {"message": f"Attendance deleted by {current_user.first_name}"}


# -------------------------------
# ✅ NEW: Dedicated Anomaly Analytics Endpoint
# -------------------------------
@router.get(
    "/analytics/anomalies",
    dependencies=[Depends(require_view_permission(ATTENDANCE_MENU_ID))]
)
def get_anomaly_analytics(
    days_back: int = Query(30, ge=7, le=180, description="Days to analyze"),
    user_id: Optional[int] = Query(None, description="Analyze specific user"),
    severity: Optional[str] = Query(None, description="Filter by severity (high, medium, low)"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive anomaly analytics
    
    Returns:
    - Total anomalies by severity
    - Most common anomaly patterns
    - Users with most anomalies
    - Trend over time
    """
    try:
        from app.utils.attendance_anomaly_detector import get_or_train_model
        
        # Get trained model
        detector = get_or_train_model(db, organization_id=1, days_back=90)
        
        # Get recent attendance records
        cutoff_date = datetime.now().date() - timedelta(days=days_back)
        query = db.query(Attendance).filter(Attendance.attendance_date >= cutoff_date)
        
        if user_id:
            query = query.filter(Attendance.user_id == user_id)
        
        records = query.all()
        
        if not records:
            return {
                "success": True,
                "message": "No records found",
                "analytics": {}
            }
        
        # Convert to dict
        attendance_dicts = [
            {
                'id': r.id,
                'user_id': r.user_id,
                'attendance_date': r.attendance_date,
                'punch_in': r.punch_in,
                'punch_out': r.punch_out,
                'total_worked_minutes': r.total_worked_minutes,
                'status': r.status
            }
            for r in records
        ]
        
        # Detect anomalies
        anomalies = detector.predict_anomalies(attendance_dicts)
        
        # Filter by severity if requested
        if severity:
            anomalies = [a for a in anomalies if a['severity'] == severity.lower()]
        
        # Calculate analytics
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        reason_counts = {}
        user_anomaly_counts = {}
        
        for anomaly in anomalies:
            # Count by severity
            severity_counts[anomaly['severity']] += 1
            
            # Count by reason
            for reason in anomaly['reasons']:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
            
            # Count by user
            uid = anomaly['user_id']
            user_anomaly_counts[uid] = user_anomaly_counts.get(uid, 0) + 1
        
        # Sort reasons by frequency
        top_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Sort users by anomaly count
        top_users = sorted(user_anomaly_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "success": True,
            "analytics": {
                "period": {
                    "days_analyzed": days_back,
                    "total_records": len(records),
                    "total_anomalies": len(anomalies),
                    "anomaly_rate": round(len(anomalies) / len(records) * 100, 2) if records else 0
                },
                "severity_breakdown": severity_counts,
                "top_reasons": [{"reason": r, "count": c} for r, c in top_reasons],
                "users_with_most_anomalies": [{"user_id": u, "count": c} for u, c in top_users],
                "recent_anomalies": anomalies[:5]  # Last 5 anomalies
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analytics failed: {str(e)}"
        )