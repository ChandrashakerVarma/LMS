from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role_id: int

class UserCreate(UserBase):   
    password: str           

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role_id: int  

class UserResponse(UserBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    inactive: bool

    class Config:             
        from_attributes = True
