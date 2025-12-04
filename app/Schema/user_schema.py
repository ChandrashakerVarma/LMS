from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

# ==========================================================
# 🔹 BASE SCHEMA — fields accepted for create/update
# ==========================================================
class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: EmailStr

    role_id: int
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    department_id: Optional[int] = None

    # NEW: Salary Structure
    salary_structure_id: Optional[int] = None

    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    relieving_date: Optional[date] = None

    address: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=100)
    inactive: Optional[bool] = False
    biometric_id: Optional[str] = Field(None, max_length=50)

    shift_roster_id: Optional[int] = None


# ==========================================================
# 🔹 CREATE SCHEMA
# ==========================================================
class UserCreate(UserBase):
    """Schema for creating a new user within an organization"""
    password: str = Field(..., min_length=6)
     # organization_id is now required (will be set from current user's org)
    # branch_id is optional but recommended



# ==========================================================
# 🔹 UPDATE SCHEMA
# ==========================================================
class UserUpdate(BaseModel):
    """Schema for updating user details"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    department_id: Optional[int] = None

    # NEW: Salary structure update allowed
    salary_structure_id: Optional[int] = None

    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    relieving_date: Optional[date] = None

    address: Optional[str] = None
    designation: Optional[str] = None
    inactive: Optional[bool] = None
    biometric_id: Optional[str] = None

    shift_roster_id: Optional[int] = None


# ==========================================================
# 🔹 RESPONSE SCHEMA — includes audit fields
# ==========================================================
class UserResponse(UserBase):
    """Standard user response"""
    id: int
    is_org_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==========================================================
# 🔹 DETAILED RESPONSE — extra relationship fields
# ==========================================================
class UserDetailResponse(UserResponse):
    role_name: Optional[str] = None
    branch_name: Optional[str] = None
    organization_name: Optional[str] = None
    department_name: Optional[str] = None

    # NEW: Salary Structure name support
    salary_structure_name: Optional[str] = None

    model_config = {"from_attributes": True}


# ==========================================================
# AUTH SCHEMAS
# ==========================================================
class AuthRegister(BaseModel):
    first_name: str
    last_name: Optional[str]
    email: EmailStr
    password: str

    # Organization details (optional - will auto-create if not provided)
    organization_name: Optional[str]
    contact_phone: Optional[str]


class AuthRegisterResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: Optional[str]
    email: EmailStr
    
    # Organization info
    organization_id: int
    organization_name: str
    is_org_admin: bool

    # Subscription info
    subscription_status: str
    subscription_end_date: Optional[date]
    trial_days_remaining: Optional[int]

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
