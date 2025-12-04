from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


# ============================================================
# USER BASE
# ============================================================
class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: EmailStr

    role_id: int
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    department_id: Optional[int] = None

    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    relieving_date: Optional[date] = None

    address: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=100)
    inactive: Optional[bool] = False
    biometric_id: Optional[str] = Field(None, max_length=50)
    shift_roster_id: Optional[int] = None

    # NEW FIELD → BRANCH / WFH / ANY
    attendance_mode: Optional[str] = Field("BRANCH", max_length=20)


# ============================================================
# CREATE USER
# ============================================================
class UserCreate(UserBase):
    """New user creation (within an organization)"""
    password: str = Field(..., min_length=6)
    # organization_id auto-set from logged-in user


# ============================================================
# UPDATE USER
# ============================================================
class UserUpdate(BaseModel):
    """Update user details"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None

    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    department_id: Optional[int] = None

    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    relieving_date: Optional[date] = None

    address: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=100)
    inactive: Optional[bool] = None
    biometric_id: Optional[str] = Field(None, max_length=50)
    shift_roster_id: Optional[int] = None

    # NEW — Allow Admin to change work mode
    attendance_mode: Optional[str] = Field(None, max_length=20)


# ============================================================
# USER RESPONSE (BASIC)
# ============================================================
class UserResponse(UserBase):
    id: int
    is_org_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# USER RESPONSE (DETAILED)
# ============================================================
class UserDetailResponse(UserResponse):
    role_name: Optional[str] = None
    branch_name: Optional[str] = None
    organization_name: Optional[str] = None
    department_name: Optional[str] = None

    model_config = {"from_attributes": True}


# ============================================================
# AUTH SCHEMAS
# ============================================================
class AuthRegister(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

    organization_name: Optional[str] = Field(None, max_length=150)
    contact_phone: Optional[str] = Field(None, max_length=20)


class AuthRegisterResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr

    organization_id: int
    organization_name: str
    is_org_admin: bool

    subscription_status: str
    subscription_end_date: Optional[date] = None
    trial_days_remaining: Optional[int] = None

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
