from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# ---------- Role ----------
class RoleResponse(BaseModel):
    id: int
    role: Optional[str] = None  # Make role optional

    class Config:
        orm_mode = True


# ---------- Progress ----------
class ProgressResponse(BaseModel):
    id: int
    course_id: int
    progress: Optional[int] = 0  # Default to 0 if missing

    class Config:
        orm_mode = True


# ---------- User ----------
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role_id: int


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    inactive: bool

    role: Optional[RoleResponse] = None  # nested role info
    progress: List[ProgressResponse] = []  # nested progress list

    class Config:
        orm_mode = True
