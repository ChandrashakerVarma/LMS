<<<<<<< HEAD
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
    first_name: str
    last_name: str
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
=======
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

# ---------------------- Base Schema ----------------------
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    address: Optional[str] = None
    designation: Optional[str] = None
    date_of_birth: Optional[date] = None         # Only date, not datetime
    joining_date: Optional[datetime] = None      # Full datetime
    relieving_date: Optional[datetime] = None    # Optional datetime, can be null


# ---------------------- Create Schema ----------------------
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)    # Ensure password >= 6 chars


# ---------------------- Update Schema ----------------------
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    address: Optional[str] = None
    designation: Optional[str] = None
    inactive: Optional[bool] = None
    date_of_birth: Optional[date] = None
    joining_date: Optional[datetime] = None
    relieving_date: Optional[datetime] = None


# ---------------------- Response Schema ----------------------
class UserResponse(UserBase):
    id: int
    inactive: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Related names (IDs or names)
    role_name: Optional[str] = None
    branch_name: Optional[str] = None
    organization_name: Optional[str] = None

    class Config:
        orm_mode = True


# ==========================================================
# 🔹 AUTH SCHEMAS (for register & login)
# ==========================================================

class AuthRegister(BaseModel):
    """Used in /auth/register"""
    name: str
    email: EmailStr
    role_id: Optional[int] = None
    password: str = Field(..., min_length=6)


class AuthRegisterResponse(BaseModel):
    """Response for /auth/register"""
    name: str
    email: EmailStr
    role_id: Optional[int] = None

    class Config:
        orm_mode = True
>>>>>>> origin/main
