from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
import io

from app.database import get_db
from app.models.video_m import Video
from app.schema.video_schema import VideoCreate, VideoUpdate, VideoResponse
from app.utils.S3 import generate_s3_key, generate_presigned_post, generate_presigned_get, upload_fileobj


router = APIRouter(prefix="/videos", tags=["Videos"])


# -----------------------------------------------------------
# 1️⃣ Generate a presigned POST URL (for browser uploads)
# -----------------------------------------------------------
class PresignRequest(BaseModel):
    filename: str
    content_type: str
    course_id: int


@router.post("/upload/presign")
def presign_upload(req: PresignRequest):
    key = generate_s3_key(req.filename, req.course_id)
    presigned = generate_presigned_post(key=key, content_type=req.content_type)
    return {"key": key, "presigned": presigned}


# -----------------------------------------------------------
# 2️⃣ Create a new video (YouTube or S3)
# -----------------------------------------------------------
@router.post("/", response_model=VideoResponse)
def create_video(payload: VideoCreate, db: Session = Depends(get_db)):
    """
    Create a new video record.
    If youtube_url is provided, it's a YouTube video.
    If s3_key is provided, it's an S3-uploaded video.
    """
    if not payload.youtube_url and not payload.s3_key:
        raise HTTPException(400, "Either youtube_url or s3_key must be provided")

    video = Video(
        course_id=payload.course_id,
        title=payload.title,
        youtube_url=str(payload.youtube_url) if payload.youtube_url else None,
        s3_key=payload.s3_key,
        duration=payload.duration,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


# -----------------------------------------------------------
# 3️⃣ Get all videos
# -----------------------------------------------------------
@router.get("/", response_model=list[VideoResponse])
def get_all_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).all()
    return videos


# -----------------------------------------------------------
# 4️⃣ Get single video by ID
# -----------------------------------------------------------
@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(404, "Video not found")
    return video


# -----------------------------------------------------------
# 5️⃣ Get presigned URL for playback (S3 or YouTube)
# -----------------------------------------------------------
@router.get("/{video_id}/playback-url")
def get_video_playback(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(404, "Video not found")

    # YouTube video → return the YouTube URL directly
    if video.youtube_url:
        return {"type": "youtube", "url": video.youtube_url}

    # S3 video → return a presigned GET URL
    if video.s3_key:
        url = generate_presigned_get(video.s3_key, expires_in=3600)
        return {"type": "s3", "url": url}

    raise HTTPException(400, "No video source found (missing s3_key or youtube_url)")


# -----------------------------------------------------------
# 6️⃣ Upload video file directly to S3 (via FastAPI)
# -----------------------------------------------------------
@router.post("/upload/server", response_model=VideoResponse)
async def upload_via_server(
    course_id: int,
    title: str = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload file directly to S3 (from the backend) and create a video record.
    """
    key = generate_s3_key(file.filename, course_id)
    data = await file.read()
    upload_fileobj(io.BytesIO(data), key, content_type=file.content_type)

    video = Video(course_id=course_id, title=title, s3_key=key)
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


# -----------------------------------------------------------
# 7️⃣ Update video
# -----------------------------------------------------------
@router.put("/{video_id}", response_model=VideoResponse)
def update_video(video_id: int, payload: VideoUpdate, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(404, "Video not found")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(video, field, value)

    db.commit()
    db.refresh(video)
    return video


# -----------------------------------------------------------
# 8️⃣ Delete video
# -----------------------------------------------------------
@router.delete("/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(404, "Video not found")

    db.delete(video)
    db.commit()
    return {"message": f"Video {video_id} deleted successfully"}

