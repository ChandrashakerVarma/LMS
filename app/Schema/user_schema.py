from pydantic import BaseModel, EmailStr
from datetime import datetime

# ---------- Role ----------
class RoleResponse(BaseModel):
    id: int
    role: str

    class Config:
        orm_mode = True


# ---------- Progress ----------
class ProgressResponse(BaseModel):
    id: int
    course_id: int
    progress: int  # percentage progress (0–100)

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
    created_at: datetime | None = None
    updated_at: datetime | None = None
    inactive: bool

    role: RoleResponse | None = None  # nested role info
    progress: list[ProgressResponse] = []  # nested progress list

    class Config:
        orm_mode = True
