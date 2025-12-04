from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.ai_models.face_utils import register_user_face

router = APIRouter(prefix="/face", tags=["Face Recognition"])


@router.post("/register")
async def register_face(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    bytes_data = await file.read()
    try:
        result = register_user_face(db, current_user.id, bytes_data)
        return {"status": "success", "face_id": result.id}
    except Exception as e:
        raise HTTPException(400, str(e))
