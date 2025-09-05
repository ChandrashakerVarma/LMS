from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from urllib.parse import urlparse, parse_qs


# Helper validation for YouTube
def _validate_youtube_url(url: str) -> str:
    parsed = urlparse(url)
    hostname = parsed.netloc.lower()

    if "youtube.com" not in hostname and "youtu.be" not in hostname:
        raise ValueError("youtube_url must be a valid YouTube link.")

    if "youtu.be" in hostname:
        if not parsed.path or parsed.path.strip("/") == "":
            raise ValueError("Invalid YouTube short URL.")
    elif "youtube.com" in hostname:
        if parsed.path.startswith("/watch"):
            qs = parse_qs(parsed.query)
            if "v" not in qs:
                raise ValueError("YouTube watch URL must include a video ID (v parameter).")
        elif parsed.path.startswith(("/embed/", "/shorts/")):
            if len(parsed.path.strip("/").split("/")) < 2:
                raise ValueError("Invalid YouTube embed/shorts URL.")
    return url


class CourseBase(BaseModel):
    title: str
    instructor: str
    level: str = "beginner"
    youtube_url: str
    duration: Optional[int] = None
    price: float = 0.0

    # validate youtube link
    @validator("youtube_url")
    @classmethod
    def check_youtube(cls, v: str) -> str:
        return _validate_youtube_url(v)


class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True   # 👈 Pydantic v1 style

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    level: Optional[str] = None
    youtube_url: Optional[str] = None
    duration: Optional[int] = None

    class Config:
        orm_mode = True


