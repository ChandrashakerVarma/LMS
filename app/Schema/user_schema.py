from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

# Nested schemas
class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ProgressResponse(BaseModel):
    id: int
    progress_name: str  # replace with actual fields in your Progress model

    class Config:
        from_attributes = True

# Base schema for shared fields
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role_id: Optional[int] = None
    date_of_birth: Optional[datetime] = None
    joining_date: Optional[datetime] = None
    relieving_date: Optional[datetime] = None
    address: Optional[str] = None
    #photo: Optional[str] = None
    designation: Optional[str] = None

# Schema for creating a user
class UserCreate(UserBase):
    password: str  # plain password, will be hashed in service layer

# Schema for returning a user
class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    inactive: bool = False

    role: Optional[RoleResponse] = None  # nested role info
    progress: List[ProgressResponse] = []  # nested progress list

    class Config:
        from_attribute = True
