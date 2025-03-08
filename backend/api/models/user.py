from pydantic import BaseModel, EmailStr, Field
from humps import camelize
from typing import Optional
from datetime import datetime
import uuid
from .base import BaseModelConfig

class UserCreate(BaseModelConfig):
    email: EmailStr
    full_name: str
    password: str
 

class UserInDB(BaseModelConfig):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    role: str = "user"
    created_at: datetime = None
    updated_at: datetime = None

class User(BaseModelConfig):
    user_id: str
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime

class UserUpdate(BaseModelConfig):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
