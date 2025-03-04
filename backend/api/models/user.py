from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserInDB(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    role: str = "user"
    created_at: datetime = None
    updated_at: datetime = None

class User(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None