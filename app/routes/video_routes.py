from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional


from app.database import get_db
from app.models.video_m import Video
from app.models.course_m import Course
from app.schema.video_schema import VideoCreate, VideoResponse, VideoUpdate
from app.dependencies import get_current_user, require_org_admin

# Permission dependencies
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/videos", tags=["Videos"])

MENU_ID = 32


# ---------------- CREATE ----------------
@router.post(
    "/", 
    response_model=VideoResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(MENU_ID))]
)
def create_video(
    video: VideoCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(require_org_admin)
):
    course = db.query(Course).filter(Course.id == video.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    new_video = Video(**video.dict())
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    # Update course duration
    total_duration = db.query(func.sum(Video.duration)).filter(Video.course_id == video.course_id).scalar() or 0.0
    course.duration = total_duration
    db.commit()
    db.refresh(course)

    return VideoResponse.from_orm(
        db.query(Video).options(joinedload(Video.checkpoints)).filter(Video.id == new_video.id).first()
    )


# ---------------- LIST ----------------
@router.get("/", response_model=List[VideoResponse])
async def get_all_videos(
    # ✅ NEW: Fuzzy search parameters
    use_fuzzy_search: bool = Query(False, description="Enable fuzzy search"),
    fuzzy_query: Optional[str] = Query(None, description="Fuzzy search query"),
    fuzzy_threshold: int = Query(70, ge=50, le=100),
    
    # Your existing parameters
    course_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all videos with OPTIONAL fuzzy search
    
    Searches across: title, youtube_url
    """
    
    query = db.query(Video)
    
    # Your existing filters
    if course_id:
        query = query.filter(Video.course_id == course_id)
    
    if use_fuzzy_search and fuzzy_query:
        from app.utils.fuzzy_search import apply_fuzzy_search_to_query
        
        search_fields = ['title', 'youtube_url']
        field_weights = {
            'title': 2.5,
            'youtube_url': 1.0
        }
        
        videos = apply_fuzzy_search_to_query(
            base_query=query,
            model_class=Video,
            fuzzy_query=fuzzy_query,
            search_fields=search_fields,
            field_weights=field_weights,
            fuzzy_threshold=fuzzy_threshold
        )
        
        videos = videos[skip:skip + limit]
    else:
        videos = query.offset(skip).limit(limit).all()
    
    return videos
# ---------------- GET BY ID ----------------
@router.get(
    "/{video_id}", 
    response_model=VideoResponse,
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).options(joinedload(Video.checkpoints)).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoResponse.from_orm(video)


# ---------------- UPDATE ----------------
@router.put(
    "/{video_id}", 
    response_model=VideoResponse,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def update_video(
    video_id: int, 
    payload: VideoUpdate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(require_org_admin)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(video, key, value)
    db.commit()
    db.refresh(video)

    # Recalculate course duration
    course = db.query(Course).filter(Course.id == video.course_id).first()
    if course:
        total_duration = db.query(func.sum(Video.duration)).filter(Video.course_id == video.course_id).scalar() or 0.0
        course.duration = total_duration
        db.commit()
        db.refresh(course)

    return VideoResponse.from_orm(
        db.query(Video).options(joinedload(Video.checkpoints)).filter(Video.id == video.id).first()
    )


# ---------------- DELETE ----------------
@router.delete(
    "/{video_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_video(
    video_id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(require_org_admin)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    course_id = video.course_id
    db.delete(video)
    db.commit()

    # Recalculate course duration
    course = db.query(Course).filter(Course.id == course_id).first()
    if course:
        total_duration = db.query(func.sum(Video.duration)).filter(Video.course_id == course_id).scalar() or 0.0
        course.duration = total_duration
        db.commit()
        db.refresh(course)

    return {"message": "Video deleted successfully"}
